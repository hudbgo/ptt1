import { useEffect, useState } from 'react'
import axios from 'axios'

const API_URL = 'http://127.0.0.1:8000'

export default function App() {
  const [target, setTarget] = useState('')
  const [operator, setOperator] = useState('analyst-1')
  const [loading, setLoading] = useState(false)
  const [analyses, setAnalyses] = useState([])
  const [error, setError] = useState('')

  const loadAnalyses = async () => {
    const { data } = await axios.get(`${API_URL}/analyses`)
    setAnalyses(data)
  }

  useEffect(() => {
    loadAnalyses().catch(() => setError('No se pudo cargar el historial.'))
  }, [])

  const startAnalysis = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      await axios.post(`${API_URL}/analyses`, { target })
      setTarget('')
      await loadAnalyses()
    } catch {
      setError('Error al analizar objetivo. Verifica backend y formato de IP/dominio.')
    } finally {
      setLoading(false)
    }
  }

  const decideProposal = async (id, approved) => {
    await axios.patch(`${API_URL}/proposals/${id}`, { approved, approved_by: operator })
    await loadAnalyses()
  }

  const executeProposal = async (proposal) => {
    const actionInfo = `Se ejecutará acción segura: ${proposal.action_key}\nParámetros: ${JSON.stringify(proposal.action_params)}`
    if (!window.confirm(actionInfo)) return
    try {
      await axios.post(`${API_URL}/execute`, {
        proposal_id: proposal.id,
        executed_by: operator,
      })
      await loadAnalyses()
    } catch {
      setError('No se pudo ejecutar la propuesta aprobada.')
    }
  }

  return (
    <div className="page">
      <header>
        <h1>Pentest AI Assist</h1>
        <p>Asistente de pentesting con IA y aprobación humana obligatoria.</p>
      </header>

      <section className="panel">
        <form onSubmit={startAnalysis}>
          <label>Operador</label>
          <input value={operator} onChange={(e) => setOperator(e.target.value)} required />
          <label>IP o dominio objetivo autorizado</label>
          <div className="row">
            <input
              value={target}
              onChange={(e) => setTarget(e.target.value)}
              placeholder="ej: 192.168.1.15 o ejemplo.com"
              required
            />
            <button disabled={loading}>{loading ? 'Analizando...' : 'Iniciar análisis IA'}</button>
          </div>
        </form>
        {error && <p className="error">{error}</p>}
      </section>

      <section className="grid">
        {analyses.map((analysis) => (
          <article className="card" key={analysis.id}>
            <div className="card-head">
              <h3>{analysis.target}</h3>
              <span className="risk">Riesgo: {analysis.risk_score.toFixed(1)}</span>
            </div>
            <p><strong>Puertos:</strong> {analysis.open_ports.join(', ') || 'ninguno'}</p>
            <p><strong>Fingerprint:</strong> {analysis.service_fingerprint}</p>

            {analysis.vulnerabilities.map((vuln) => (
              <div className="vuln" key={vuln.id}>
                <h4>{vuln.name} <small>({vuln.severity})</small></h4>
                <p>{vuln.description}</p>
                <p>Confianza IA: {(vuln.confidence * 100).toFixed(0)}%</p>

                {vuln.proposals.map((proposal) => (
                  <div className="proposal" key={proposal.id}>
                    <p><strong>Propuesta:</strong> {proposal.title}</p>
                    <p>{proposal.action_plan}</p>
                    <p><strong>Acción permitida:</strong> {proposal.action_key} | {JSON.stringify(proposal.action_params)}</p>
                    <div className="actions">
                      <button onClick={() => decideProposal(proposal.id, true)}>Aprobar</button>
                      <button className="ghost" onClick={() => decideProposal(proposal.id, false)}>Rechazar</button>
                      {proposal.approved === true && (
                        <button onClick={() => executeProposal(proposal)}>Ejecutar</button>
                      )}
                      <span>
                        Estado: {proposal.approved === null ? 'pendiente' : proposal.approved ? 'aprobada' : 'rechazada'}
                      </span>
                    </div>
                    {proposal.execution_status !== 'not_executed' && (
                      <div>
                        <p><strong>Ejecución:</strong> {proposal.execution_status}</p>
                        {proposal.execution_result && <pre>{proposal.execution_result}</pre>}
                        {proposal.execution_error && <p className="error">{proposal.execution_error}</p>}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            ))}
          </article>
        ))}
      </section>
    </div>
  )
}
