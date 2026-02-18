import React, { useState } from 'react'
import { 
  SparklesIcon, 
  ChartBarIcon,
  LightBulbIcon,
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon
} from '@heroicons/react/24/outline'

export default function XGBoostPredictionPanel({ analysisId }) {
  const [prediction, setPrediction] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const runPrediction = async () => {
    setLoading(true)
    setError(null)
    
    try {
      const response = await fetch(`/api/xgboost/predict/${analysisId}`, {
        method: 'POST'
      })
      
      if (!response.ok) {
        throw new Error('Failed to get prediction')
      }
      
      const data = await response.json()
      setPrediction(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const getPerformanceColor = (score) => {
    if (score >= 0.8) return 'text-green-600'
    if (score >= 0.6) return 'text-yellow-600'
    return 'text-red-600'
  }

  const getPerformanceLabel = (score) => {
    if (score >= 0.8) return 'Excelente'
    if (score >= 0.6) return 'Bom'
    if (score >= 0.4) return 'Médio'
    return 'Necessita Melhoria'
  }

  const getFeatureInterpretation = (featureName, shapValue, featureValues) => {
    const val = featureValues?.[featureName]
    const isPositive = shapValue > 0
    const strength = Math.abs(shapValue)
    const intensityWord = strength > 0.05 ? 'significativamente' : strength > 0.02 ? 'moderadamente' : 'ligeiramente'

    const interpretations = {
      'pressure_density': {
        pos: `Densidade de pressão elevada (${val?.toFixed(2) || '—'}) indica que a equipa aplica pressão concentrada sobre o portador da bola, ${intensityWord} aumentando a eficácia tática. A unidade defensiva fecha os espaços de forma eficiente.`,
        neg: `Densidade de pressão baixa (${val?.toFixed(2) || '—'}) sugere que a equipa tem dificuldade em aplicar pressão concentrada perto da bola, ${intensityWord} reduzindo o controlo tático. Recomenda-se uma pressão mais coordenada.`
      },
      'pressure_effectiveness': {
        pos: `A eficácia da pressão é elevada (${val?.toFixed(2) || '—'}), o que significa que as ações de pressão ${intensityWord} contribuem para a recuperação da posse de bola. A equipa converte bem a pressão defensiva em recuperações.`,
        neg: `A eficácia da pressão é baixa (${val?.toFixed(2) || '—'}), indicando que as ações de pressão não se traduzem ${intensityWord} em recuperações de bola. A equipa pressiona mas não consegue ganhar a bola de forma consistente.`
      },
      'defensive_coverage': {
        pos: `A cobertura defensiva (${val?.toFixed(2) || '—'}) é forte — a equipa cobre ${intensityWord} as linhas de passe e zonas perigosas de forma eficaz, limitando as opções ofensivas do adversário.`,
        neg: `A cobertura defensiva (${val?.toFixed(2) || '—'}) é fraca — a equipa deixa espaços em zonas críticas, ${intensityWord} expondo a defesa a passes em profundidade e mudanças de flanco.`
      },
      'formation_stability': {
        pos: `A estabilidade da formação (${val?.toFixed(2) || '—'}) é elevada, o que significa que a equipa ${intensityWord} mantém a sua forma tática durante as transições. Os jogadores mantêm a disciplina posicional.`,
        neg: `A estabilidade da formação (${val?.toFixed(2) || '—'}) é baixa — a equipa ${intensityWord} perde a sua forma durante as transições, criando vulnerabilidades estruturais que o adversário pode explorar.`
      },
      'line_compactness': {
        pos: `A compacidade da linha defensiva (${val?.toFixed(2) || '—'}) é apertada, ${intensityWord} reduzindo o espaço entre as linhas defensivas. Isto dificulta ao adversário jogar entre linhas.`,
        neg: `A compacidade da linha defensiva (${val?.toFixed(2) || '—'}) é frouxa — o espaço entre linhas é grande, ${intensityWord} permitindo ao adversário receber a bola em bolsas de espaço perigosas.`
      },
      'avg_distance_to_ball': {
        pos: `A distância média à bola (${val?.toFixed(1) || '—'}m) é curta, ${intensityWord} indicando que a equipa se mantém próxima da bola e aplica pressão imediata sobre o portador.`,
        neg: `A distância média à bola (${val?.toFixed(1) || '—'}m) é grande, ${intensityWord} sugerindo que a equipa se posiciona demasiado recuada ou reage lentamente ao movimento da bola, dando tempo ao adversário.`
      },
      'min_distance_to_ball': {
        pos: `A distância mínima à bola (${val?.toFixed(1) || '—'}m) é muito curta, ${intensityWord} mostrando que pelo menos um jogador aborda consistentemente o portador da bola com marcação apertada.`,
        neg: `A distância mínima à bola (${val?.toFixed(1) || '—'}m) é demasiado grande — nenhum jogador está suficientemente perto para pressionar o portador, ${intensityWord} dando liberdade ao adversário para jogar em frente.`
      },
      'pressure_ratio': {
        pos: `O rácio de pressão (${val?.toFixed(2) || '—'}) favorece a equipa da casa, ${intensityWord} indicando uma vantagem dominante na pressão sobre o adversário.`,
        neg: `O rácio de pressão (${val?.toFixed(2) || '—'}) é desfavorável — o adversário aplica pressão mais eficaz, ${intensityWord} limitando a capacidade da equipa de construir a partir de trás.`
      },
      'defensive_width': {
        pos: `A largura defensiva (${val?.toFixed(1) || '—'}m) é equilibrada, ${intensityWord} cobrindo o campo lateralmente mantendo a compacidade. A equipa defende os flancos sem se sobreexpor.`,
        neg: `A largura defensiva (${val?.toFixed(1) || '—'}m) é problemática — ou demasiado estreita (expondo os flancos) ou demasiado larga (criando espaços centrais), ${intensityWord} enfraquecendo a estrutura defensiva.`
      },
      'avg_gap_between_defenders': {
        pos: `O espaço médio entre defesas (${val?.toFixed(1) || '—'}m) é bem controlado, ${intensityWord} dificultando aos atacantes encontrar espaço entre a linha defensiva.`,
        neg: `O espaço médio entre defesas (${val?.toFixed(1) || '—'}m) é demasiado grande, ${intensityWord} criando espaços exploráveis por atacantes rápidos.`
      },
      'defensive_line_depth': {
        pos: `A profundidade da linha defensiva (${val?.toFixed(1) || '—'}m) está bem posicionada, ${intensityWord} equilibrando a armadilha do fora-de-jogo com a proteção do espaço atrás da defesa.`,
        neg: `A profundidade da linha defensiva (${val?.toFixed(1) || '—'}m) está mal posicionada — ou demasiado alta (vulnerável a bolas nas costas) ou demasiado recuada (convidando pressão), ${intensityWord} prejudicando o equilíbrio defensivo.`
      },
      'ball_pressure_intensity': {
        pos: `A intensidade de pressão sobre a bola (${val?.toFixed(0) || '—'}) é elevada, ${intensityWord} mostrando que a equipa compromete vários jogadores para pressionar a zona da bola de forma agressiva.`,
        neg: `A intensidade de pressão sobre a bola (${val?.toFixed(0) || '—'}) é baixa — a equipa não compromete jogadores suficientes na zona de pressão, ${intensityWord} permitindo progressão fácil da bola pelo adversário.`
      },
      'overall_avg_distance': {
        pos: `A distância média global (${val?.toFixed(1) || '—'}m) é compacta, ${intensityWord} indicando que ambas as equipas operam em proximidade — sinal de jogo intenso e disputado.`,
        neg: `A distância média global (${val?.toFixed(1) || '—'}m) é dispersa, ${intensityWord} sugerindo uma fase de baixa intensidade ou uma equipa demasiado passiva no seu posicionamento.`
      },
      'max_gap': {
        pos: `O espaço máximo (${val?.toFixed(1) || '—'}m) está controlado, ${intensityWord} significando que mesmo o maior espaço entre defesas é gerível e não facilmente explorável.`,
        neg: `O espaço máximo (${val?.toFixed(1) || '—'}m) é perigosamente grande, ${intensityWord} criando uma vulnerabilidade crítica que atacantes habilidosos podem explorar com corridas ou passes.`
      },
      'min_gap': {
        pos: `O espaço mínimo (${val?.toFixed(1) || '—'}m) mostra marcação apertada entre pelo menos dois defesas, ${intensityWord} proporcionando uma base sólida na linha defensiva.`,
        neg: `O espaço mínimo (${val?.toFixed(1) || '—'}m) ainda é relativamente largo, ${intensityWord} sugerindo que a linha defensiva carece de coesão mesmo no seu ponto mais apertado.`
      }
    }

    const interp = interpretations[featureName]
    if (!interp) {
      return isPositive
        ? `Este parâmetro contribui ${intensityWord} de forma positiva para a pontuação de desempenho tático.`
        : `Este parâmetro reduz ${intensityWord} a pontuação de desempenho tático.`
    }
    return isPositive ? interp.pos : interp.neg
  }

  const generateGameSummary = (pred) => {
    if (!pred) return ''
    const score = pred.prediction
    const positives = pred.top_positive_features || []
    const negatives = pred.top_negative_features || []
    const adjustment = ((score - pred.base_value) * 100).toFixed(1)
    const aboveBelow = score > pred.base_value ? 'acima' : 'abaixo'

    let summary = ''

    // Avaliação global
    if (score >= 0.8) {
      summary += `A equipa demonstra um desempenho tático excelente (${(score * 100).toFixed(1)}%), operando ${Math.abs(adjustment)}% ${aboveBelow} da média de referência. Isto indica uma equipa bem organizada e disciplinada que executa o seu plano de jogo de forma eficaz em todas as fases do jogo.`
    } else if (score >= 0.6) {
      summary += `A equipa apresenta um bom desempenho tático (${(score * 100).toFixed(1)}%), ${Math.abs(adjustment)}% ${aboveBelow} da referência. A estrutura global é sólida, embora existam áreas onde ajustes táticos poderiam gerar melhorias significativas.`
    } else if (score >= 0.4) {
      summary += `O desempenho tático da equipa é médio (${(score * 100).toFixed(1)}%), situando-se ${Math.abs(adjustment)}% ${aboveBelow} da referência. Embora alguns elementos táticos funcionem adequadamente, a equipa precisa de corrigir várias fragilidades estruturais para competir a um nível superior.`
    } else {
      summary += `O desempenho tático da equipa está abaixo das expectativas (${(score * 100).toFixed(1)}%), ${Math.abs(adjustment)}% ${aboveBelow} da referência. É necessária uma reestruturação tática significativa em múltiplas dimensões para melhorar o rendimento competitivo.`
    }

    // Pontos fortes
    if (positives.length > 0) {
      const topStrengths = positives.slice(0, 3).map(f => f.feature.replace(/_/g, ' ')).join(', ')
      summary += `\n\nPontos fortes: As principais vantagens táticas da equipa provêm de ${topStrengths}. `
      if (positives[0]?.shap_value > 0.05) {
        summary += `Em particular, ${positives[0].feature.replace(/_/g, ' ')} é um fator de destaque, contribuindo substancialmente para a pontuação global e deve ser mantido como prioridade tática.`
      } else {
        summary += `Estes fatores contribuem positivamente mas nenhum domina — a força da equipa reside na execução equilibrada e não numa área excecional.`
      }
    }

    // Pontos a melhorar
    if (negatives.length > 0) {
      const topWeaknesses = negatives.slice(0, 3).map(f => f.feature.replace(/_/g, ' ')).join(', ')
      summary += `\n\nÁreas a melhorar: As principais vulnerabilidades táticas são ${topWeaknesses}. `
      if (Math.abs(negatives[0]?.shap_value) > 0.05) {
        summary += `Corrigir ${negatives[0].feature.replace(/_/g, ' ')} deve ser a prioridade máxima nos treinos, pois tem o maior impacto negativo na eficácia tática global.`
      } else {
        summary += `Os impactos negativos são relativamente pequenos, sugerindo que a equipa não tem fragilidades críticas mas pode ainda refinar estas áreas para ganhos marginais.`
      }
    } else {
      summary += `\n\nNão foram identificadas fragilidades táticas significativas pelo modelo — todos os parâmetros medidos contribuem positiva ou neutralmente para a pontuação de desempenho.`
    }

    // Recomendação para o treinador
    summary += `\n\nRecomendação para o treinador: `
    if (score >= 0.7) {
      summary += `Manter a abordagem tática atual focando na consistência. Utilizar a análise de vídeo para reforçar os padrões positivos identificados acima e garantir que são replicados ao longo dos jogos.`
    } else if (score >= 0.5) {
      summary += `Focar as sessões de treino nas fragilidades identificadas, preservando os pontos fortes existentes. Considerar exercícios táticos que visem especificamente a coordenação da pressão e a forma defensiva.`
    } else {
      summary += `Recomenda-se uma revisão tática abrangente. Considerar simplificar o plano de jogo para focar primeiro na organização defensiva e depois introduzir gradualmente padrões de pressão mais complexos à medida que a estrutura base da equipa melhora.`
    }

    return summary
  }

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-6">
      <div className="flex items-center justify-between mb-4">
        <h4 className="text-lg font-medium text-gray-900 flex items-center">
          <SparklesIcon className="h-5 w-5 mr-2 text-purple-600" />
          Predição Tática XGBoost + SHAP
        </h4>
        <button
          onClick={runPrediction}
          disabled={loading}
          className="px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700 disabled:bg-gray-400 flex items-center"
        >
          {loading ? (
            <>
              <svg className="animate-spin h-4 w-4 mr-2" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>
              A prever...
            </>
          ) : (
            'Executar Predição ML'
          )}
        </button>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
          <p className="text-red-800">{error}</p>
        </div>
      )}

      {prediction && !prediction.error && (
        <div className="space-y-6">
          {/* Performance Prediction */}
          <div className="bg-gradient-to-r from-purple-50 to-blue-50 border border-purple-200 rounded-lg p-6">
            <div className="text-center">
              <p className="text-sm text-gray-600 mb-2">Desempenho Tático Previsto</p>
              <div className={`text-6xl font-bold ${getPerformanceColor(prediction.prediction)}`}>
                {(prediction.prediction * 100).toFixed(1)}%
              </div>
              <p className="text-lg font-medium text-gray-700 mt-2">
                {getPerformanceLabel(prediction.prediction)}
              </p>
              <p className="text-sm text-gray-500 mt-1">
                Confiança: {(prediction.prediction_confidence * 100).toFixed(0)}%
              </p>
            </div>
          </div>

          {/* SHAP Feature Importance */}
          <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
            <h5 className="font-medium text-gray-900 mb-3 flex items-center">
              <ChartBarIcon className="h-5 w-5 mr-2 text-blue-600" />
              Contribuições SHAP por Parâmetro
            </h5>
            
            {/* Top Positive Features */}
            {prediction.top_positive_features && prediction.top_positive_features.length > 0 && (
              <div className="mb-4">
                <p className="text-sm font-medium text-green-700 mb-2 flex items-center">
                  <ArrowTrendingUpIcon className="h-4 w-4 mr-1" />
                  Parâmetros com Impacto Positivo
                </p>
                <div className="space-y-2">
                  {prediction.top_positive_features.map((feature, idx) => (
                    <div key={idx} className="bg-white p-3 rounded border space-y-1">
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium text-gray-800 capitalize">{feature.feature.replace(/_/g, ' ')}</span>
                        <div className="flex items-center">
                          <div className="w-32 bg-gray-200 rounded-full h-2 mr-2">
                            <div 
                              className="bg-green-500 h-2 rounded-full" 
                              style={{ width: `${Math.min(100, Math.abs(feature.shap_value) * 200)}%` }}
                            />
                          </div>
                          <span className="text-xs font-medium text-green-600">
                            +{feature.shap_value.toFixed(3)}
                          </span>
                        </div>
                      </div>
                      <p className="text-xs text-gray-500 leading-relaxed">
                        {getFeatureInterpretation(feature.feature, feature.shap_value, prediction.feature_values)}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Top Negative Features */}
            {prediction.top_negative_features && prediction.top_negative_features.length > 0 && (
              <div>
                <p className="text-sm font-medium text-red-700 mb-2 flex items-center">
                  <ArrowTrendingDownIcon className="h-4 w-4 mr-1" />
                  Parâmetros com Impacto Negativo
                </p>
                <div className="space-y-2">
                  {prediction.top_negative_features.map((feature, idx) => (
                    <div key={idx} className="bg-white p-3 rounded border space-y-1">
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium text-gray-800 capitalize">{feature.feature.replace(/_/g, ' ')}</span>
                        <div className="flex items-center">
                          <div className="w-32 bg-gray-200 rounded-full h-2 mr-2">
                            <div 
                              className="bg-red-500 h-2 rounded-full" 
                              style={{ width: `${Math.min(100, Math.abs(feature.shap_value) * 200)}%` }}
                            />
                          </div>
                          <span className="text-xs font-medium text-red-600">
                            {feature.shap_value.toFixed(3)}
                          </span>
                        </div>
                      </div>
                      <p className="text-xs text-gray-500 leading-relaxed">
                        {getFeatureInterpretation(feature.feature, feature.shap_value, prediction.feature_values)}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* ML Insights — Game-Level Summary */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-5">
            <h5 className="font-medium text-blue-900 mb-4 flex items-center text-base">
              <LightBulbIcon className="h-5 w-5 mr-2" />
              Insights de Machine Learning — Resumo do Jogo
            </h5>
            <div className="space-y-3 text-sm text-blue-800">
              <div className="flex items-center space-x-4 pb-3 border-b border-blue-200">
                <div>
                  <span className="text-xs text-blue-600">Modelo</span>
                  <p className="font-medium">XGBoost + SHAP</p>
                </div>
                <div>
                  <span className="text-xs text-blue-600">Referência</span>
                  <p className="font-medium">{(prediction.base_value * 100).toFixed(1)}%</p>
                </div>
                <div>
                  <span className="text-xs text-blue-600">Ajuste</span>
                  <p className="font-medium">
                    {prediction.prediction > prediction.base_value ? '+' : ''}{((prediction.prediction - prediction.base_value) * 100).toFixed(1)}%
                  </p>
                </div>
                <div>
                  <span className="text-xs text-blue-600">Confiança</span>
                  <p className="font-medium">{(prediction.prediction_confidence * 100).toFixed(0)}%</p>
                </div>
              </div>
              <div className="whitespace-pre-line leading-relaxed text-blue-900">
                {generateGameSummary(prediction)}
              </div>
            </div>
          </div>

          {/* Feature Values */}
          {prediction.feature_values && Object.keys(prediction.feature_values).length > 0 && (
            <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
              <h5 className="font-medium text-gray-900 mb-3">Valores Reais dos Parâmetros</h5>
              <div className="grid grid-cols-2 gap-2 text-sm">
                {Object.entries(prediction.feature_values).slice(0, 8).map(([key, value]) => (
                  <div key={key} className="bg-white p-2 rounded border">
                    <span className="text-gray-600">{key.replace(/_/g, ' ')}:</span>
                    <span className="font-medium text-gray-900 ml-2">
                      {typeof value === 'number' ? value.toFixed(2) : value}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {prediction && prediction.error && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <p className="text-yellow-800 font-medium">{prediction.error}</p>
          <p className="text-yellow-700 text-sm mt-2">{prediction.message}</p>
        </div>
      )}

      {!prediction && !loading && (
        <div className="text-center py-8 text-gray-500">
          <SparklesIcon className="h-12 w-12 mx-auto mb-3 text-gray-400" />
          <p>Clique em "Executar Predição ML" para obter a predição de desempenho XGBoost</p>
          <p className="text-sm mt-2">
            Utiliza machine learning para prever a eficácia tática com explicações SHAP
          </p>
        </div>
      )}
    </div>
  )
}
