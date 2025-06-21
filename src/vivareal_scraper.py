#!/usr/bin/env python3
"""
Scraper para coleta de dados do VivaReal (mercado tradicional)
Projeto: Comparação de Valores de Mercado de Imóveis
Autores: Fernando Lobo, Fernando Torres, Marcio Ferreira
Professor: Otavio Calaça
"""

import cloudscraper
import pandas as pd
import time
import random
from bs4 import BeautifulSoup
from urllib.parse import urljoin, quote
import json
import os
from datetime import datetime
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class VivaRealScraper:
    def __init__(self, use_proxy=False, proxy_config=None):
        """
        Inicializa o scraper para VivaReal
        
        Args:
            use_proxy (bool): Se deve usar proxy residencial
            proxy_config (dict): Configurações do proxy
        """
        self.scraper = cloudscraper.create_scraper()
        self.base_url = "https://www.vivareal.com.br"
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
        
    def search_imoveis(self, cidade="sao-paulo", tipo="apartamento", max_pages=5):
        """
        Busca imóveis por cidade e tipo
        
        Args:
            cidade (str): Nome da cidade
            tipo (str): Tipo de imóvel (apartamento, casa, etc.)
            max_pages (int): Número máximo de páginas
            
        Returns:
            list: Lista de URLs de imóveis
        """
        urls = []
        
        for page in range(1, max_pages + 1):
            try:
                # Construir URL de busca
                search_url = f"{self.base_url}/venda/{cidade}/{tipo}/?pagina={page}"
                logger.info(f"Buscando página {page}: {search_url}")
                
                response = self.scraper.get(search_url)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Buscar links de imóveis (ajustar seletor conforme estrutura)
                imovel_links = soup.find_all('a', href=True)
                
                for link in imovel_links:
                    href = link.get('href')
                    if href and '/imovel/' in href:
                        full_url = urljoin(self.base_url, href)
                        if full_url not in urls:
                            urls.append(full_url)
                
                # Delay entre requisições
                time.sleep(random.uniform(3, 6))
                
            except Exception as e:
                logger.error(f"Erro ao buscar página {page}: {e}")
                continue
                
        logger.info(f"Encontradas {len(urls)} URLs de imóveis")
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
            
            # Estrutura de dados (ajustar conforme HTML real)
            data = {
                'url': url,
                'titulo': self._safe_extract(soup, 'h1'),
                'preco': self._extract_price(soup),
                'endereco': self._extract_address(soup),
                'bairro': self._safe_extract(soup, '.neighborhood'),
                'cidade': self._safe_extract(soup, '.city'),
                'area': self._extract_area(soup),
                'quartos': self._extract_number(soup, '.bedrooms'),
                'banheiros': self._extract_number(soup, '.bathrooms'),
                'vagas': self._extract_number(soup, '.parking'),
                'tipo_imovel': self._safe_extract(soup, '.property-type'),
                'descricao': self._safe_extract(soup, '.description'),
                'caracteristicas': self._extract_features(soup),
                'preco_m2': None,  # Será calculado depois
                'data_coleta': datetime.now().isoformat(),
                'fonte': 'vivareal'
            }
            
            # Calcular preço por m² se possível
            if data['preco'] and data['area']:
                data['preco_m2'] = data['preco'] / data['area']
            
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
    
    def _extract_price(self, soup):
        """Extrai preço do imóvel"""
        try:
            # Tentar diferentes seletores para preço
            price_selectors = ['.price', '.valor', '[data-testid="price"]', '.js-price']
            
            for selector in price_selectors:
                price_element = soup.select_one(selector)
                if price_element:
                    price_text = price_element.get_text(strip=True)
                    # Limpar e converter preço
                    import re
                    price_clean = re.sub(r'[^\d,.]', '', price_text)
                    price_clean = price_clean.replace(',', '.')
                    return float(price_clean) if price_clean else None
        except:
            return None
    
    def _extract_address(self, soup):
        """Extrai endereço completo"""
        try:
            address_selectors = ['.address', '.endereco', '[data-testid="address"]']
            
            for selector in address_selectors:
                address = self._safe_extract(soup, selector)
                if address:
                    return address
        except:
            return None
    
    def _extract_area(self, soup):
        """Extrai área do imóvel"""
        try:
            area_selectors = ['.area', '.metragem', '[data-testid="area"]']
            
            for selector in area_selectors:
                area_text = self._safe_extract(soup, selector)
                if area_text:
                    import re
                    area_match = re.search(r'(\d+(?:,\d+)?)\s*m²?', area_text)
                    if area_match:
                        return float(area_match.group(1).replace(',', '.'))
        except:
            return None
    
    def _extract_number(self, soup, selector):
        """Extrai números (quartos, banheiros, etc.)"""
        try:
            text = self._safe_extract(soup, selector)
            if text:
                import re
                number_match = re.search(r'(\d+)', text)
                return int(number_match.group(1)) if number_match else None
        except:
            return None
    
    def _extract_features(self, soup):
        """Extrai características do imóvel"""
        try:
            features = []
            feature_elements = soup.select('.feature, .caracteristica, .amenity')
            
            for element in feature_elements:
                feature_text = element.get_text(strip=True)
                if feature_text:
                    features.append(feature_text)
            
            return features if features else None
        except:
            return None
    
    def scrape_mercado_tradicional(self, cidades=None, tipos=None, max_pages=3, max_imoveis=100):
        """
        Executa o scraping do mercado tradicional
        
        Args:
            cidades (list): Lista de cidades para buscar
            tipos (list): Lista de tipos de imóveis
            max_pages (int): Máximo de páginas por busca
            max_imoveis (int): Máximo de imóveis para coletar
        """
        if not cidades:
            cidades = ["sao-paulo", "rio-de-janeiro", "goiania", "brasilia"]
        
        if not tipos:
            tipos = ["apartamento", "casa"]
        
        logger.info("Iniciando coleta de dados do mercado tradicional")
        
        all_urls = []
        
        # Coletar URLs para cada combinação cidade/tipo
        for cidade in cidades:
            for tipo in tipos:
                logger.info(f"Buscando {tipo} em {cidade}")
                urls = self.search_imoveis(cidade, tipo, max_pages)
                all_urls.extend(urls)
                
                # Delay entre buscas
                time.sleep(random.uniform(5, 10))
        
        # Remover duplicatas
        all_urls = list(set(all_urls))
        
        # Limitar número de imóveis se necessário
        if len(all_urls) > max_imoveis:
            all_urls = all_urls[:max_imoveis]
        
        # Extrair dados de cada imóvel
        for i, url in enumerate(all_urls, 1):
            logger.info(f"Processando imóvel {i}/{len(all_urls)}: {url}")
            
            data = self.extract_imovel_data(url)
            if data:
                self.data.append(data)
            
            # Delay entre requisições
            time.sleep(random.uniform(4, 8))
        
        logger.info(f"Coleta finalizada. {len(self.data)} imóveis coletados")
    
    def save_data(self, filename=None):
        """
        Salva os dados coletados
        
        Args:
            filename (str): Nome do arquivo (opcional)
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"vivareal_data_{timestamp}.json"
        
        filepath = os.path.join('../data', filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Dados salvos em {filepath}")
        
        # Também salvar como CSV
        if self.data:
            df = pd.DataFrame(self.data)
            csv_filename = filepath.replace('.json', '.csv')
            df.to_csv(csv_filename, index=False, encoding='utf-8')
            logger.info(f"Dados também salvos em {csv_filename}")

def main():
    """Função principal"""
    # Configuração de proxy (exemplo)
    proxy_config = {
        'http': 'http://username:password@proxy-server:port',
        'https': 'https://username:password@proxy-server:port'
    }
    
    # Inicializar scraper
    scraper = VivaRealScraper(use_proxy=False, proxy_config=proxy_config)
    
    # Executar scraping
    scraper.scrape_mercado_tradicional(
        cidades=["sao-paulo", "goiania"],
        tipos=["apartamento", "casa"],
        max_pages=2,
        max_imoveis=30
    )
    
    # Salvar dados
    scraper.save_data()

if __name__ == "__main__":
    main()

