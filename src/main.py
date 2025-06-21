#!/usr/bin/env python3
"""
Pipeline principal para coleta e análise de dados de imóveis
Projeto: Comparação de Valores de Mercado de Imóveis
Autores: Fernando Lobo, Fernando Torres, Marcio Ferreira
Professor: Otavio Calaça
"""

import os
import sys
import logging
import argparse
from datetime import datetime

# Adicionar o diretório src ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from leilao_scraper import LeilaoScraper
from vivareal_scraper import VivaRealScraper
from data_analyzer import ImovelAnalyzer

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('../data/pipeline.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ImovelPipeline:
    def __init__(self, use_proxy=False, proxy_config=None):
        """
        Inicializa o pipeline completo
        
        Args:
            use_proxy (bool): Se deve usar proxy residencial
            proxy_config (dict): Configurações do proxy
        """
        self.use_proxy = use_proxy
        self.proxy_config = proxy_config or {}
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Criar diretórios necessários
        os.makedirs('../data', exist_ok=True)
        os.makedirs('../data/raw', exist_ok=True)
        os.makedirs('../data/processed', exist_ok=True)
        os.makedirs('../data/graficos', exist_ok=True)
        
        logger.info("Pipeline inicializado")
    
    def run_leilao_scraping(self, max_pages=3, max_imoveis=50):
        """
        Executa a coleta de dados de leilões
        
        Args:
            max_pages (int): Máximo de páginas para processar
            max_imoveis (int): Máximo de imóveis para coletar
        """
        try:
            logger.info("=== INICIANDO COLETA DE LEILÕES ===")
            
            scraper = LeilaoScraper(
                use_proxy=self.use_proxy,
                proxy_config=self.proxy_config
            )
            
            scraper.scrape_leiloes(max_pages=max_pages, max_imoveis=max_imoveis)
            
            # Salvar com timestamp
            filename = f"leiloes_data_{self.timestamp}.json"
            scraper.save_data(filename)
            
            logger.info("Coleta de leilões concluída")
            return f"../data/{filename}"
            
        except Exception as e:
            logger.error(f"Erro na coleta de leilões: {e}")
            return None
    
    def run_vivareal_scraping(self, cidades=None, tipos=None, max_pages=2, max_imoveis=30):
        """
        Executa a coleta de dados do VivaReal
        
        Args:
            cidades (list): Lista de cidades
            tipos (list): Lista de tipos de imóveis
            max_pages (int): Máximo de páginas por busca
            max_imoveis (int): Máximo de imóveis para coletar
        """
        try:
            logger.info("=== INICIANDO COLETA DO VIVAREAL ===")
            
            if not cidades:
                cidades = ["sao-paulo", "goiania"]
            
            if not tipos:
                tipos = ["apartamento", "casa"]
            
            scraper = VivaRealScraper(
                use_proxy=self.use_proxy,
                proxy_config=self.proxy_config
            )
            
            scraper.scrape_mercado_tradicional(
                cidades=cidades,
                tipos=tipos,
                max_pages=max_pages,
                max_imoveis=max_imoveis
            )
            
            # Salvar com timestamp
            filename = f"vivareal_data_{self.timestamp}.json"
            scraper.save_data(filename)
            
            logger.info("Coleta do VivaReal concluída")
            return f"../data/{filename}"
            
        except Exception as e:
            logger.error(f"Erro na coleta do VivaReal: {e}")
            return None
    
    def run_analysis(self, leiloes_file=None, vivareal_file=None):
        """
        Executa a análise dos dados coletados
        
        Args:
            leiloes_file (str): Caminho para arquivo de leilões
            vivareal_file (str): Caminho para arquivo do VivaReal
        """
        try:
            logger.info("=== INICIANDO ANÁLISE DOS DADOS ===")
            
            analyzer = ImovelAnalyzer()
            
            # Carregar dados
            analyzer.load_data(
                leiloes_file=leiloes_file,
                tradicional_file=vivareal_file
            )
            
            # Processar dados
            analyzer.clean_data()
            
            # Gerar análises
            stats = analyzer.generate_statistics()
            analyzer.create_visualizations()
            analyzer.generate_report()
            
            logger.info("Análise concluída")
            return stats
            
        except Exception as e:
            logger.error(f"Erro na análise: {e}")
            return None
    
    def run_full_pipeline(self, config=None):
        """
        Executa o pipeline completo
        
        Args:
            config (dict): Configurações do pipeline
        """
        if not config:
            config = {
                'leiloes': {'max_pages': 2, 'max_imoveis': 30},
                'vivareal': {
                    'cidades': ["sao-paulo", "goiania"],
                    'tipos': ["apartamento", "casa"],
                    'max_pages': 2,
                    'max_imoveis': 20
                }
            }
        
        try:
            logger.info("=== INICIANDO PIPELINE COMPLETO ===")
            
            # 1. Coleta de leilões
            leiloes_file = self.run_leilao_scraping(
                max_pages=config['leiloes']['max_pages'],
                max_imoveis=config['leiloes']['max_imoveis']
            )
            
            # 2. Coleta do VivaReal
            vivareal_file = self.run_vivareal_scraping(
                cidades=config['vivareal']['cidades'],
                tipos=config['vivareal']['tipos'],
                max_pages=config['vivareal']['max_pages'],
                max_imoveis=config['vivareal']['max_imoveis']
            )
            
            # 3. Análise dos dados
            if leiloes_file or vivareal_file:
                stats = self.run_analysis(
                    leiloes_file=leiloes_file,
                    vivareal_file=vivareal_file
                )
                
                logger.info("=== PIPELINE CONCLUÍDO COM SUCESSO ===")
                return {
                    'leiloes_file': leiloes_file,
                    'vivareal_file': vivareal_file,
                    'statistics': stats
                }
            else:
                logger.error("Nenhum dado foi coletado")
                return None
                
        except Exception as e:
            logger.error(f"Erro no pipeline: {e}")
            return None
    
    def create_sample_data(self):
        """
        Cria dados de exemplo para demonstração
        """
        try:
            logger.info("Criando dados de exemplo...")
            
            import pandas as pd
            import numpy as np
            
            # Dados de exemplo para leilões
            np.random.seed(42)
            n_leiloes = 50
            
            leiloes_data = {
                'titulo': [f'Imóvel Leilão {i+1}' for i in range(n_leiloes)],
                'preco': np.random.normal(300000, 100000, n_leiloes),
                'area': np.random.normal(80, 30, n_leiloes),
                'tipo_imovel': np.random.choice(['apartamento', 'casa', 'comercial'], n_leiloes),
                'endereco': [f'Rua Exemplo {i+1}' for i in range(n_leiloes)],
                'fonte': ['leilao'] * n_leiloes
            }
            
            df_leiloes = pd.DataFrame(leiloes_data)
            df_leiloes['preco_m2'] = df_leiloes['preco'] / df_leiloes['area']
            df_leiloes = df_leiloes[df_leiloes['preco'] > 0]
            df_leiloes = df_leiloes[df_leiloes['area'] > 0]
            
            # Dados de exemplo para mercado tradicional (preços mais altos)
            n_tradicional = 50
            
            tradicional_data = {
                'titulo': [f'Imóvel Tradicional {i+1}' for i in range(n_tradicional)],
                'preco': np.random.normal(500000, 150000, n_tradicional),
                'area': np.random.normal(85, 35, n_tradicional),
                'tipo_imovel': np.random.choice(['apartamento', 'casa', 'comercial'], n_tradicional),
                'endereco': [f'Avenida Exemplo {i+1}' for i in range(n_tradicional)],
                'fonte': ['tradicional'] * n_tradicional
            }
            
            df_tradicional = pd.DataFrame(tradicional_data)
            df_tradicional['preco_m2'] = df_tradicional['preco'] / df_tradicional['area']
            df_tradicional = df_tradicional[df_tradicional['preco'] > 0]
            df_tradicional = df_tradicional[df_tradicional['area'] > 0]
            
            # Salvar dados de exemplo
            leiloes_file = f"../data/leiloes_data_exemplo_{self.timestamp}.csv"
            tradicional_file = f"../data/vivareal_data_exemplo_{self.timestamp}.csv"
            
            df_leiloes.to_csv(leiloes_file, index=False)
            df_tradicional.to_csv(tradicional_file, index=False)
            
            logger.info(f"Dados de exemplo criados: {leiloes_file}, {tradicional_file}")
            
            # Executar análise com dados de exemplo
            stats = self.run_analysis(leiloes_file, tradicional_file)
            
            return {
                'leiloes_file': leiloes_file,
                'vivareal_file': tradicional_file,
                'statistics': stats
            }
            
        except Exception as e:
            logger.error(f"Erro ao criar dados de exemplo: {e}")
            return None

def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description='Pipeline de Análise de Imóveis')
    parser.add_argument('--mode', choices=['full', 'leiloes', 'vivareal', 'analysis', 'demo'], 
                       default='demo', help='Modo de execução')
    parser.add_argument('--use-proxy', action='store_true', help='Usar proxy residencial')
    parser.add_argument('--max-pages', type=int, default=2, help='Máximo de páginas para scraping')
    parser.add_argument('--max-imoveis', type=int, default=30, help='Máximo de imóveis para coletar')
    
    args = parser.parse_args()
    
    # Configuração de proxy (ajustar conforme necessário)
    proxy_config = {
        'http': 'http://username:password@proxy-server:port',
        'https': 'https://username:password@proxy-server:port'
    } if args.use_proxy else None
    
    # Inicializar pipeline
    pipeline = ImovelPipeline(use_proxy=args.use_proxy, proxy_config=proxy_config)
    
    try:
        if args.mode == 'demo':
            logger.info("Executando demonstração com dados de exemplo")
            result = pipeline.create_sample_data()
            
        elif args.mode == 'full':
            logger.info("Executando pipeline completo")
            config = {
                'leiloes': {'max_pages': args.max_pages, 'max_imoveis': args.max_imoveis},
                'vivareal': {
                    'cidades': ["sao-paulo", "goiania"],
                    'tipos': ["apartamento", "casa"],
                    'max_pages': args.max_pages,
                    'max_imoveis': args.max_imoveis
                }
            }
            result = pipeline.run_full_pipeline(config)
            
        elif args.mode == 'leiloes':
            logger.info("Executando apenas coleta de leilões")
            result = pipeline.run_leilao_scraping(args.max_pages, args.max_imoveis)
            
        elif args.mode == 'vivareal':
            logger.info("Executando apenas coleta do VivaReal")
            result = pipeline.run_vivareal_scraping(max_pages=args.max_pages, max_imoveis=args.max_imoveis)
            
        elif args.mode == 'analysis':
            logger.info("Executando apenas análise")
            result = pipeline.run_analysis()
        
        if result:
            logger.info("Pipeline executado com sucesso!")
            print(f"\nResultados salvos em: ../data/")
            print(f"Verifique os arquivos gerados e o relatório de análise.")
        else:
            logger.error("Pipeline falhou")
            
    except KeyboardInterrupt:
        logger.info("Pipeline interrompido pelo usuário")
    except Exception as e:
        logger.error(f"Erro inesperado: {e}")

if __name__ == "__main__":
    main()

