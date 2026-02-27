import React from 'react';

const StoreCard = ({ store, currentStoreId }) => {
    const isCurrentStore = store.store_id === currentStoreId;
    const googleMapsUrl = `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(store.address)}`;

    return (
        <div style={{
            background: isCurrentStore ? 'rgba(34,197,94,0.08)' : 'white',
            border: isCurrentStore ? '2px solid #22c55e' : '1px solid rgba(0,0,0,0.07)',
            borderRadius: '14px',
            padding: '12px 16px',
            marginBottom: '8px',
            display: 'flex',
            flexDirection: 'column',
            gap: '5px',
            boxShadow: '0 2px 8px rgba(1,102,48,0.07)',
            transition: 'all 0.2s ease',
        }}>
            {/* Header row */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <span style={{ fontSize: '18px' }}>🛒</span>
                    <span style={{ fontWeight: 700, fontSize: '14px', color: '#0d2818' }}>{store.name}</span>
                    {isCurrentStore && (
                        <span style={{
                            background: 'rgba(34,197,94,0.15)',
                            color: '#016630',
                            fontSize: '10px',
                            fontWeight: 700,
                            padding: '2px 8px',
                            borderRadius: '999px',
                            textTransform: 'uppercase',
                            letterSpacing: '0.05em'
                        }}>You are here</span>
                    )}
                </div>
                <span style={{
                    background: 'rgba(1,102,48,0.08)',
                    color: '#016630',
                    fontSize: '12px',
                    fontWeight: 700,
                    padding: '3px 10px',
                    borderRadius: '999px',
                    border: '1px solid rgba(1,102,48,0.15)',
                }}>
                    {store.distance_miles === 0 ? 'Current' : `${store.distance_miles} mi`}
                </span>
            </div>

            {/* Address */}
            <div style={{ display: 'flex', alignItems: 'flex-start', gap: '5px' }}>
                <span style={{ fontSize: '12px' }}>📍</span>
                <a
                    href={googleMapsUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    style={{ fontSize: '12px', color: '#016630', textDecoration: 'none', fontWeight: 500 }}
                >
                    {store.address}
                </a>
            </div>

            {/* Phone + hours */}
            <div style={{ display: 'flex', gap: '16px', flexWrap: 'wrap' }}>
                {store.phone && (
                    <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                        <span style={{ fontSize: '11px' }}>📞</span>
                        <span style={{ fontSize: '12px', color: '#4b7a5e' }}>{store.phone}</span>
                    </div>
                )}
                <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                    <span style={{ fontSize: '11px' }}>🕐</span>
                    <span style={{ fontSize: '12px', color: '#4b7a5e' }}>{store.hours}</span>
                </div>
            </div>
        </div>
    );
};

export default StoreCard;
