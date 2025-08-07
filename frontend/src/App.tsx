import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ApolloProvider } from '@apollo/client';
import { apolloClient } from './graphql/client';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import SensorTypes from './pages/SensorTypes';
import Locations from './pages/Locations';
import SensorsModern from './pages/SensorsModern';
import SensorReadings from './pages/SensorReadings';

function App() {
  return (
    <ApolloProvider client={apolloClient}>
      <Router>
        <Layout>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/sensor-types" element={<SensorTypes />} />
            <Route path="/locations" element={<Locations />} />
            <Route path="/sensors" element={<SensorsModern />} />
            <Route path="/readings" element={<SensorReadings />} />
          </Routes>
        </Layout>
      </Router>
    </ApolloProvider>
  );
}

export default App;
