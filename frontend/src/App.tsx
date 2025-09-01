import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ApolloProvider } from '@apollo/client';
import { apolloClient } from './graphql/client';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import SensorTypes from './pages/SensorTypes';
import Locations from './pages/Locations';
import Sensors from './pages/Sensors';
import SensorReadings from './pages/SensorReadings';
import TestPage from './pages/TestPage';
import SimpleTest from './pages/SimpleTest';

function App() {
  return (
    <ApolloProvider client={apolloClient}>
      <Router>
        <Routes>
          <Route path="/simple" element={<SimpleTest />} />
          <Route path="/*" element={
            <Layout>
              <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/sensor-types" element={<SensorTypes />} />
                <Route path="/locations" element={<Locations />} />
                <Route path="/sensors" element={<Sensors />} />
                <Route path="/readings" element={<SensorReadings />} />
                <Route path="/test" element={<TestPage />} />
              </Routes>
            </Layout>
          } />
        </Routes>
      </Router>
    </ApolloProvider>
  );
}

export default App;
