import React, { useState, useEffect } from 'react';

const InsightsPanel = () => {
    const [logs, setLogs] = useState([]);
    const [lostSales, setLostSales] = useState(0);

    useEffect(() => {
        fetch('https://smartgrocer-ai.onrender.com/api/analytics/searches')
            .then(res => res.json())
            .then(data => {
                setLogs(data.recent_logs || []); // Assuming data.recent_logs might be renamed to data.searches or similar, but keeping original state variable
                setLostSales(data.lost_sales);
            })
            .catch(err => console.error("Error fetching analytics", err)); // Keeping original error message for consistency
    }, []);

    return (
        <>
            <div className="metrics-grid">
                <div className="metric-card">
                    <div className="metric-title">Total Queries Today</div>
                    <div className="metric-value">{logs.length}</div>
                </div>
                <div className="metric-card">
                    <div className="metric-title">Lost Sales Alerts (Out of Stock)</div>
                    <div className="metric-value" style={{ color: 'var(--danger)' }}>{lostSales}</div>
                </div>
                <div className="metric-card">
                    <div className="metric-title">Avg Local Resolution Rate</div>
                    <div className="metric-value" style={{ color: 'var(--success)' }}>
                        {logs.length > 0 ? Math.round((logs.filter(l => l.found_locally).length / logs.length) * 100) : 0}%
                    </div>
                </div>
            </div>

            <div className="panel">
                <div className="panel-title">Recent Shopper Queries</div>
                <div style={{ overflowX: 'auto' }}>
                    <table className="data-table">
                        <thead>
                            <tr>
                                <th>Timestamp</th>
                                <th>Query Intent</th>
                                <th>Raw Query</th>
                                <th>Resolution</th>
                                <th>Action Taken</th>
                            </tr>
                        </thead>
                        <tbody>
                            {logs.map((log) => (
                                <tr key={log.id}>
                                    <td>{new Date(log.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</td>
                                    <td>
                                        <span className={`badge ${log.intent === 'complex_search' ? 'info' : 'warning'}`}>
                                            {log.intent.replace('_', ' ')}
                                        </span>
                                    </td>
                                    <td style={{ fontWeight: 500 }}>"{log.query}"</td>
                                    <td>
                                        {log.found_locally ? (
                                            <span className="badge success">Found Locally</span>
                                        ) : (
                                            <span className="badge danger">Out of Stock</span>
                                        )}
                                    </td>
                                    <td>
                                        {log.redirected_to_competitor ? (
                                            <span style={{ color: 'var(--primary)', fontSize: '0.9rem' }}>Redirected to Search</span>
                                        ) : (
                                            <span style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>Aisle displayed</span>
                                        )}
                                    </td>
                                </tr>
                            ))}
                            {logs.length === 0 && (
                                <tr>
                                    <td colSpan="5" style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-muted)' }}>
                                        No queries logged yet. Start asking questions on the tablet!
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        </>
    );
};

export default InsightsPanel;
