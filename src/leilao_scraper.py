#!/usr/bin/env python3
"""
Scraper para coleta de dados de leilões judiciais
Projeto: Comparação de Valores de Mercado de Imóveis
Autores: Fernando Lobo, Fernando Torres, Marcio Ferreira
Professor: Otavio Calaça
"""

import cloudscraper
import pandas as pd
import time
import random
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import json
import os
from datetime import datetime
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LeilaoScraper:
    def __init__(self, use_proxy=False, proxy_config=None):
        """
        Inicializa o scraper para leilões judiciais
        
        Args:
            use_proxy (bool): Se deve usar proxy residencial
            proxy_config (dict): Configurações do proxy
        """
        self.scraper = cloudscraper.create_scraper()
        self.base_url = "https://www.leiloesjudiciais.com.br"
        self.use_proxy = use_proxy
        self.proxy_config = proxy_config or {}
        
        if self.use_proxy and self.proxy_config:
            self.scraper.proxies = self.proxy_config
            
        # Headers para simular navegador real
        self.scraper.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        self.data = []
        
    def get_imoveis_urls(self, max_pages=5):
        """
        Coleta URLs de imóveis em leilão
        
        Args:
            max_pages (int): Número máximo de páginas para processar
            
        Returns:
            list: Lista de URLs de imóveis
        """
        urls = []
        
        for page in range(1, max_pages + 1):
            try:
                url = f"{self.base_url}/imoveis?page={page}"
                logger.info(f"Processando página {page}: {url}")
                
                response = self.scraper.get(url)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Buscar links de imóveis (ajustar seletor conforme estrutura do site)
                imovel_links = soup.find_all('a', href=True)
                
                for link in imovel_links:
                    href = link.get('href')
                    if href and '/imovel/' in href:
                        full_url = urljoin(self.base_url, href)
                        if full_url not in urls:
                            urls.append(full_url)
                
                # Delay entre requisições para ser respeitoso
                time.sleep(random.uniform(2, 5))
                
            except Exception as e:
                logger.error(f"Erro ao processar página {page}: {e}")
                continue
                
        logger.info(f"Coletadas {len(urls)} URLs de imóveis")
        return urls
    
    def extract_imovel_data(self, url):
        """
        Extrai dados de um imóvel específico
        
        Args:
            url (str): URL do imóvel
            
        Returns:
            dict: Dados do imóvel
        """
        try:
            response = self.scraper.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Estrutura básica de dados (ajustar conforme HTML real)
            data = {
                'url': url,
                'titulo': self._safe_extract(soup, 'h1'),
                'preco_inicial': self._extract_price(soup, '.preco-inicial'),
                'preco_atual': self._extract_price(soup, '.preco-atual'),
                'endereco': self._safe_extract(soup, '.endereco'),
                'area': self._extract_area(soup),
                'tipo_imovel': self._safe_extract(soup, '.tipo-imovel'),
                'data_leilao': self._safe_extract(soup, '.data-leilao'),
                'situacao': self._safe_extract(soup, '.situacao'),
                'descricao': self._safe_extract(soup, '.descricao'),
                'data_coleta': datetime.now().isoformat()
            }
            
            return data
            
        except Exception as e:
            logger.error(f"Erro ao extrair dados de {url}: {e}")
            return None
    
    def _safe_extract(self, soup, selector):
        """Extração segura de texto"""
        try:
            element = soup.select_one(selector)
            return element.get_text(strip=True) if element else None
        except:
            return None
    
    def _extract_price(self, soup, selector):
        """Extrai e limpa valores monetários"""
        try:
            price_text = self._safe_extract(soup, selector)
            if price_text:
                # Remove caracteres não numéricos exceto vírgula e ponto
                import re
                price_clean = re.sub(r'[^\d,.]', '', price_text)
                price_clean = price_clean.replace(',', '.')
                return float(price_clean) if price_clean else None
        except:
            return None
    
    def _extract_area(self, soup):
        """Extrai área do imóvel"""
        try:
            area_text = self._safe_extract(soup, '.area') or self._safe_extract(soup, '.metragem')
            if area_text:
                import re
                area_match = re.search(r'(\d+(?:,\d+)?)\s*m²?', area_text)
                if area_match:
                    return float(area_match.group(1).replace(',', '.'))
        except:
            return None
    
    def scrape_leiloes(self, max_pages=5, max_imoveis=100):
        """
        Executa o scraping completo
        
        Args:
            max_pages (int): Máximo de páginas para processar
            max_imoveis (int): Máximo de imóveis para coletar
        """
        logger.info("Iniciando coleta de dados de leilões judiciais")
        
        # Coletar URLs
        urls = self.get_imoveis_urls(max_pages)
        
        # Limitar número de imóveis se necessário
        if len(urls) > max_imoveis:
            urls = urls[:max_imoveis]
        
        # Extrair dados de cada imóvel
        for i, url in enumerate(urls, 1):
            logger.info(f"Processando imóvel {i}/{len(urls)}: {url}")
            
            data = self.extract_imovel_data(url)
            if data:
                self.data.append(data)
            
            # Delay entre requisições
            time.sleep(random.uniform(3, 7))
        
        logger.info(f"Coleta finalizada. {len(self.data)} imóveis coletados")
    
    def save_data(self, filename=None):
        """
        Salva os dados coletados
        
        Args:
            filename (str): Nome do arquivo (opcional)
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"leiloes_data_{timestamp}.json"
        
        filepath = os.path.join('../data', filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Dados salvos em {filepath}")
        
        # Também salvar como CSV para análise
        if self.data:
            df = pd.DataFrame(self.data)
            csv_filename = filepath.replace('.json', '.csv')
            df.to_csv(csv_filename, index=False, encoding='utf-8')
            logger.info(f"Dados também salvos em {csv_filename}")

def main():
    """Função principal"""
    # Configuração de proxy (exemplo - ajustar conforme necessário)
    proxy_config = {
        'http': 'http://username:password@proxy-server:port',
        'https': 'https://username:password@proxy-server:port'
    }
    
    # Inicializar scraper (use_proxy=True se tiver proxy configurado)
    scraper = LeilaoScraper(use_proxy=False, proxy_config=proxy_config)
    
    # Executar scraping
    scraper.scrape_leiloes(max_pages=3, max_imoveis=50)
    
    # Salvar dados
    scraper.save_data()

if __name__ == "__main__":
    main()

