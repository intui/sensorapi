import React from 'react';

const TestPage: React.FC = () => {
  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold text-gray-900 mb-4">Test Page</h1>
      <p className="text-gray-600">This is a simple test page to verify React is working.</p>
      <div className="mt-4 p-4 bg-blue-100 rounded">
        <p>If you can see this, React is rendering correctly!</p>
      </div>
    </div>
  );
};

export default TestPage;