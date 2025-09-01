import React from 'react';

const SimpleTest: React.FC = () => {
  console.log('SimpleTest component is rendering');
  
  return (
    <div style={{ padding: '20px', backgroundColor: '#f0f0f0', minHeight: '100vh' }}>
      <h1 style={{ color: 'red', fontSize: '24px' }}>SIMPLE TEST - NO APOLLO</h1>
      <p>If you can see this, React is working!</p>
      <div style={{ backgroundColor: 'yellow', padding: '10px', margin: '10px 0' }}>
        This is a test without any GraphQL dependencies.
      </div>
    </div>
  );
};

export default SimpleTest;