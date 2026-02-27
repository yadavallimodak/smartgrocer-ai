import React from 'react';

const InventoryCard = ({ item }) => {
  const displayName = item.name || 'Grocery Item';
  const displaySize = item.size ? ` · ${item.size}` : '';
  const displayPrice = typeof item.price === 'number' && item.price > 0
    ? `$${item.price.toFixed(2)}`
    : 'See in-store';
  const displayAisle = item.aisle && item.aisle !== 'TBD' ? `Aisle ${item.aisle}` : 'Ask an associate';
  const displayLocation = item.store_address || (item.location_id ? `Store #${item.location_id}` : null);

  return (
    <div className="inventory-card">
      {item.image && (
        <img
          src={item.image}
          alt={displayName}
          style={{ width: '64px', height: '64px', objectFit: 'contain', borderRadius: '6px', flexShrink: 0 }}
          onError={e => { e.target.style.display = 'none'; }}
        />
      )}
      <div className="item-info" style={{ flex: 1 }}>
        <h3 style={{ margin: 0, fontSize: '0.95rem' }}>{displayName}{displaySize}</h3>
        <p style={{ margin: '2px 0', color: '#94a3b8', fontSize: '0.85rem' }}>
          {item.category}
        </p>
        <p style={{ margin: '2px 0', fontWeight: '600', color: '#a78bfa' }}>
          {displayPrice}
        </p>
      </div>
      <div className="item-stats" style={{ display: 'flex', flexDirection: 'column', gap: '0.3rem', alignItems: 'flex-end' }}>
        <div className="aisle-badge">{displayAisle}</div>
        {displayLocation && (
          <div style={{ backgroundColor: '#1e293b', color: '#94a3b8', padding: '0.2rem 0.5rem', borderRadius: '4px', fontSize: '0.75rem' }}>
            📍 {displayLocation}
          </div>
        )}
        <div className={`stock-status ${item.stock > 0 ? '' : 'out'}`}>
          {item.stock > 0 ? 'In Stock' : 'Out of Stock'}
        </div>
      </div>
    </div>
  );
};

export default InventoryCard;
