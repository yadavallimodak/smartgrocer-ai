import React from 'react';

const OutofStockMap = ({ response }) => {
    return (
        <div className="map-container">
            <div style={{ padding: '1.5rem', background: 'rgba(255,255,255,0.05)' }}>
                <h3 style={{ color: 'var(--accent-alert)', marginBottom: '0.5rem' }}>Item Out of Stock</h3>
                <p>{response.message}</p>
                <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginTop: '0.5rem' }}>
                    Search Radius: {response.search_radius}
                </p>
            </div>

            <div className="alternatives-list">
                {response.alternatives && response.alternatives.map((store, idx) => (
                    <div key={idx} className="alternative-store">
                        <div className="store-details">
                            <h4>{store.store}</h4>
                            <p>{store.address}</p>
                            <p style={{ color: 'var(--accent)', marginTop: '0.2rem', fontSize: '0.9rem' }}>
                                Status: {store.availability}
                            </p>
                        </div>
                        <div className="store-distance">
                            {store.distance}
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default OutofStockMap;
