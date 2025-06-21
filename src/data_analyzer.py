#!/usr/bin/env python3
"""
Análise comparativa de dados de imóveis
Projeto: Comparação de Valores de Mercado de Imóveis
Autores: Fernando Lobo, Fernando Torres, Marcio Ferreira
Professor: Otavio Calaça
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import json
import os
from datetime import datetime
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuração para gráficos em português
plt.rcParams['font.size'] = 12
plt.rcParams['figure.figsize'] = (12, 8)
sns.set_style("whitegrid")
sns.set_palette("husl")

class ImovelAnalyzer:
    def __init__(self):
        """Inicializa o analisador de dados"""
        self.df_leiloes = None
        self.df_tradicional = None
        self.df_combined = None
        
    def load_data(self, leiloes_file=None, tradicional_file=None):
        """
        Carrega os dados dos arquivos
        
        Args:
            leiloes_file (str): Caminho para arquivo de leilões
            tradicional_file (str): Caminho para arquivo do mercado tradicional
        """
        try:
            # Carregar dados de leilões
            if leiloes_file and os.path.exists(leiloes_file):
                if leiloes_file.endswith('.json'):
                    with open(leiloes_file, 'r', encoding='utf-8') as f:
                        leiloes_data = json.load(f)
                    self.df_leiloes = pd.DataFrame(leiloes_data)
                else:
                    self.df_leiloes = pd.read_csv(leiloes_file)
                
                self.df_leiloes['fonte'] = 'leilao'
                logger.info(f"Carregados {len(self.df_leiloes)} registros de leilões")
            
            # Carregar dados do mercado tradicional
            if tradicional_file and os.path.exists(tradicional_file):
                if tradicional_file.endswith('.json'):
                    with open(tradicional_file, 'r', encoding='utf-8') as f:
                        tradicional_data = json.load(f)
                    self.df_tradicional = pd.DataFrame(tradicional_data)
                else:
                    self.df_tradicional = pd.read_csv(tradicional_file)
                
                self.df_tradicional['fonte'] = 'tradicional'
                logger.info(f"Carregados {len(self.df_tradicional)} registros do mercado tradicional")
            
        except Exception as e:
            logger.error(f"Erro ao carregar dados: {e}")
    
    def clean_data(self):
        """Limpa e padroniza os dados"""
        try:
            # Limpar dados de leilões
            if self.df_leiloes is not None:
                self.df_leiloes = self._clean_dataframe(self.df_leiloes, 'leilao')
            
            # Limpar dados do mercado tradicional
            if self.df_tradicional is not None:
                self.df_tradicional = self._clean_dataframe(self.df_tradicional, 'tradicional')
            
            # Combinar datasets
            self._combine_datasets()
            
            logger.info("Limpeza de dados concluída")
            
        except Exception as e:
            logger.error(f"Erro na limpeza de dados: {e}")
    
    def _clean_dataframe(self, df, fonte):
        """Limpa um dataframe específico"""
        df_clean = df.copy()
        
        # Padronizar colunas de preço
        if fonte == 'leilao':
            # Para leilões, usar preço atual ou inicial
            df_clean['preco'] = df_clean.get('preco_atual', df_clean.get('preco_inicial'))
        
        # Converter tipos de dados
        numeric_columns = ['preco', 'area', 'quartos', 'banheiros', 'vagas']
        for col in numeric_columns:
            if col in df_clean.columns:
                df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
        
        # Calcular preço por m² se não existir
        if 'preco_m2' not in df_clean.columns or df_clean['preco_m2'].isna().all():
            df_clean['preco_m2'] = df_clean['preco'] / df_clean['area']
        
        # Remover outliers extremos
        if 'preco_m2' in df_clean.columns:
            Q1 = df_clean['preco_m2'].quantile(0.01)
            Q3 = df_clean['preco_m2'].quantile(0.99)
            df_clean = df_clean[(df_clean['preco_m2'] >= Q1) & (df_clean['preco_m2'] <= Q3)]
        
        # Padronizar tipos de imóveis
        if 'tipo_imovel' in df_clean.columns:
            df_clean['tipo_imovel'] = df_clean['tipo_imovel'].str.lower().str.strip()
            df_clean['tipo_imovel'] = df_clean['tipo_imovel'].replace({
                'apartamento': 'apartamento',
                'casa': 'casa',
                'comercial': 'comercial',
                'terreno': 'terreno'
            })
        
        return df_clean
    
    def _combine_datasets(self):
        """Combina os datasets de leilões e mercado tradicional"""
        datasets = []
        
        if self.df_leiloes is not None:
            datasets.append(self.df_leiloes)
        
        if self.df_tradicional is not None:
            datasets.append(self.df_tradicional)
        
        if datasets:
            self.df_combined = pd.concat(datasets, ignore_index=True, sort=False)
            logger.info(f"Dataset combinado criado com {len(self.df_combined)} registros")
    
    def generate_statistics(self):
        """Gera estatísticas descritivas"""
        if self.df_combined is None:
            logger.error("Dados não carregados")
            return
        
        try:
            stats = {}
            
            # Estatísticas por fonte
            for fonte in self.df_combined['fonte'].unique():
                df_fonte = self.df_combined[self.df_combined['fonte'] == fonte]
                
                stats[fonte] = {
                    'total_imoveis': len(df_fonte),
                    'preco_medio': df_fonte['preco'].mean(),
                    'preco_mediano': df_fonte['preco'].median(),
                    'preco_m2_medio': df_fonte['preco_m2'].mean(),
                    'preco_m2_mediano': df_fonte['preco_m2'].median(),
                    'area_media': df_fonte['area'].mean(),
                }
            
            # Calcular diferenças percentuais
            if 'leilao' in stats and 'tradicional' in stats:
                stats['comparacao'] = {
                    'diferenca_preco_medio': ((stats['tradicional']['preco_medio'] - stats['leilao']['preco_medio']) / stats['tradicional']['preco_medio']) * 100,
                    'diferenca_preco_m2_medio': ((stats['tradicional']['preco_m2_medio'] - stats['leilao']['preco_m2_medio']) / stats['tradicional']['preco_m2_medio']) * 100,
                }
            
            # Salvar estatísticas
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            stats_file = f"../data/estatisticas_{timestamp}.json"
            
            with open(stats_file, 'w', encoding='utf-8') as f:
                json.dump(stats, f, ensure_ascii=False, indent=2, default=str)
            
            logger.info(f"Estatísticas salvas em {stats_file}")
            return stats
            
        except Exception as e:
            logger.error(f"Erro ao gerar estatísticas: {e}")
            return None
    
    def create_visualizations(self):
        """Cria visualizações dos dados"""
        if self.df_combined is None:
            logger.error("Dados não carregados")
            return
        
        try:
            # Criar diretório para gráficos
            os.makedirs('../data/graficos', exist_ok=True)
            
            # 1. Comparação de preços por m²
            plt.figure(figsize=(12, 8))
            sns.boxplot(data=self.df_combined, x='fonte', y='preco_m2')
            plt.title('Comparação de Preços por m² - Leilões vs Mercado Tradicional')
            plt.ylabel('Preço por m² (R$)')
            plt.xlabel('Fonte')
            plt.savefig('../data/graficos/comparacao_preco_m2.png', dpi=300, bbox_inches='tight')
            plt.close()
            
            # 2. Distribuição de preços por tipo de imóvel
            if 'tipo_imovel' in self.df_combined.columns:
                plt.figure(figsize=(14, 8))
                sns.boxplot(data=self.df_combined, x='tipo_imovel', y='preco_m2', hue='fonte')
                plt.title('Distribuição de Preços por Tipo de Imóvel')
                plt.ylabel('Preço por m² (R$)')
                plt.xlabel('Tipo de Imóvel')
                plt.xticks(rotation=45)
                plt.savefig('../data/graficos/preco_por_tipo.png', dpi=300, bbox_inches='tight')
                plt.close()
            
            # 3. Histograma de preços
            plt.figure(figsize=(12, 8))
            for fonte in self.df_combined['fonte'].unique():
                data = self.df_combined[self.df_combined['fonte'] == fonte]['preco_m2'].dropna()
                plt.hist(data, alpha=0.7, label=fonte, bins=30)
            
            plt.title('Distribuição de Preços por m²')
            plt.xlabel('Preço por m² (R$)')
            plt.ylabel('Frequência')
            plt.legend()
            plt.savefig('../data/graficos/distribuicao_precos.png', dpi=300, bbox_inches='tight')
            plt.close()
            
            # 4. Gráfico de barras com médias
            medias = self.df_combined.groupby('fonte')['preco_m2'].mean()
            
            plt.figure(figsize=(10, 6))
            bars = plt.bar(medias.index, medias.values)
            plt.title('Preço Médio por m² - Comparação entre Fontes')
            plt.ylabel('Preço Médio por m² (R$)')
            plt.xlabel('Fonte')
            
            # Adicionar valores nas barras
            for bar in bars:
                height = bar.get_height()
                plt.text(bar.get_x() + bar.get_width()/2., height,
                        f'R$ {height:,.0f}',
                        ha='center', va='bottom')
            
            plt.savefig('../data/graficos/preco_medio_comparacao.png', dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info("Visualizações criadas em ../data/graficos/")
            
        except Exception as e:
            logger.error(f"Erro ao criar visualizações: {e}")
    
    def generate_report(self):
        """Gera relatório final da análise"""
        if self.df_combined is None:
            logger.error("Dados não carregados")
            return
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = f"../data/relatorio_analise_{timestamp}.md"
            
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write("# Relatório de Análise Comparativa de Imóveis\n\n")
                f.write(f"**Data da Análise:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n")
                
                # Resumo dos dados
                f.write("## Resumo dos Dados\n\n")
                f.write(f"- **Total de imóveis analisados:** {len(self.df_combined)}\n")
                
                for fonte in self.df_combined['fonte'].unique():
                    count = len(self.df_combined[self.df_combined['fonte'] == fonte])
                    f.write(f"- **{fonte.title()}:** {count} imóveis\n")
                
                f.write("\n")
                
                # Estatísticas principais
                stats = self.generate_statistics()
                if stats:
                    f.write("## Estatísticas Principais\n\n")
                    
                    for fonte, data in stats.items():
                        if fonte != 'comparacao':
                            f.write(f"### {fonte.title()}\n")
                            f.write(f"- Preço médio: R$ {data['preco_medio']:,.2f}\n")
                            f.write(f"- Preço médio por m²: R$ {data['preco_m2_medio']:,.2f}\n")
                            f.write(f"- Área média: {data['area_media']:.1f} m²\n\n")
                    
                    if 'comparacao' in stats:
                        f.write("### Comparação\n")
                        f.write(f"- Diferença no preço médio: {stats['comparacao']['diferenca_preco_medio']:.1f}%\n")
                        f.write(f"- Diferença no preço por m²: {stats['comparacao']['diferenca_preco_m2_medio']:.1f}%\n\n")
                
                # Conclusões
                f.write("## Conclusões\n\n")
                f.write("1. Os dados coletados permitem uma análise comparativa entre leilões e mercado tradicional\n")
                f.write("2. As visualizações geradas facilitam a compreensão das diferenças de preços\n")
                f.write("3. O projeto demonstra a viabilidade do pipeline de extração automatizada\n\n")
                
                f.write("## Arquivos Gerados\n\n")
                f.write("- Gráficos de comparação em `data/graficos/`\n")
                f.write("- Estatísticas detalhadas em formato JSON\n")
                f.write("- Dados brutos em formato CSV e JSON\n")
            
            logger.info(f"Relatório gerado em {report_file}")
            
        except Exception as e:
            logger.error(f"Erro ao gerar relatório: {e}")

def main():
    """Função principal"""
    analyzer = ImovelAnalyzer()
    
    # Carregar dados (ajustar caminhos conforme necessário)
    analyzer.load_data(
        leiloes_file="../data/leiloes_data.csv",
        tradicional_file="../data/vivareal_data.csv"
    )
    
    # Limpar e processar dados
    analyzer.clean_data()
    
    # Gerar análises
    analyzer.generate_statistics()
    analyzer.create_visualizations()
    analyzer.generate_report()
    
    logger.info("Análise concluída!")

if __name__ == "__main__":
    main()

