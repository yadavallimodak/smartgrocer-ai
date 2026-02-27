import React, { useState, useEffect } from 'react';

const DeviceGrid = () => {
    const [devices, setDevices] = useState([]);

    useEffect(() => {
        fetch('https://smartgrocer-ai.onrender.com/api/analytics/devices')
            .then(res => res.json())
            .then(data => setDevices(data))
            .catch(err => console.error("Error fetching devices:", err));
    }, []);

    return (
        <div className="devices-grid">
            {devices.map((device) => {
                const lastSeen = new Date(device.last_seen);
                const isOnline = device.status === 'online' && (new Date() - lastSeen) < 30000; // Online if seen in last 30s

                return (
                    <div key={device.device_id} className="device-card">
                        <div className="device-header">
                            <h3 style={{ fontSize: '1.2rem', fontWeight: 600 }}>{device.device_id}</h3>
                            <div className={`device - status - indicator ${isOnline ? 'online' : ''} `} title={isOnline ? 'Online' : 'Offline'}></div>
                        </div>

                        <span className={`badge ${isOnline ? 'success' : 'danger'} `}>
                            {isOnline ? 'Active' : 'Offline'}
                        </span>

                        <div className="device-stats">
                            <div>
                                <span style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-muted)' }}>Battery</span>
                                <span style={{ color: 'var(--text-main)', fontWeight: 500 }}>{device.battery_level}%</span>
                            </div>
                            <div>
                                <span style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-muted)' }}>Last Ping</span>
                                <span style={{ color: 'var(--text-main)', fontWeight: 500 }}>
                                    {lastSeen.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                </span>
                            </div>
                        </div>

                        <div style={{ marginTop: '1.5rem', display: 'flex', gap: '0.5rem' }}>
                            <button style={{
                                background: 'rgba(59, 130, 246, 0.1)',
                                color: 'var(--primary)',
                                border: '1px solid rgba(59, 130, 246, 0.2)',
                                padding: '0.4rem 0.8rem',
                                borderRadius: '6px',
                                cursor: 'pointer',
                                fontSize: '0.9rem',
                                flex: 1
                            }}>
                                Restart Agent
                            </button>
                            <button style={{
                                background: 'rgba(255, 255, 255, 0.05)',
                                color: 'var(--text-main)',
                                border: '1px solid rgba(255, 255, 255, 0.1)',
                                padding: '0.4rem 0.8rem',
                                borderRadius: '6px',
                                cursor: 'pointer',
                                fontSize: '0.9rem',
                                flex: 1
                            }}>
                                OTA Update
                            </button>
                        </div>
                    </div>
                );
            })}

            {devices.length === 0 && (
                <div style={{ padding: '2rem', color: 'var(--text-muted)', background: 'var(--bg-panel)', borderRadius: '12px', gridColumn: '1 / -1', textAlign: 'center' }}>
                    No tablets registered yet. Tablets will auto-register on heartbeat.
                </div>
            )}
        </div>
    );
};

export default DeviceGrid;
