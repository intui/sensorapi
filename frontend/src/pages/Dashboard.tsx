import React from 'react';
import { useQuery } from '@apollo/client';
import { GET_SENSORS, GET_SENSOR_TYPES, GET_LOCATIONS } from '../graphql/queries';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';
import { Database, MapPin, Thermometer, Activity } from 'lucide-react';

const Dashboard: React.FC = () => {
  const { data: sensorsData, loading: sensorsLoading, error: sensorsError } = useQuery(GET_SENSORS);
  const { data: sensorTypesData, loading: typesLoading } = useQuery(GET_SENSOR_TYPES);
  const { data: locationsData, loading: locationsLoading } = useQuery(GET_LOCATIONS);

  if (sensorsLoading || typesLoading || locationsLoading) return <LoadingSpinner />;
  if (sensorsError) return <ErrorMessage message={sensorsError.message} />;

  const totalSensors = sensorsData?.sensors?.length || 0;
  const onlineSensors = sensorsData?.sensors?.filter((s: any) => s.isOnline)?.length || 0;
  const totalSensorTypes = sensorTypesData?.sensorTypes?.length || 0;
  const totalLocations = locationsData?.locations?.length || 0;

  const stats = [
    {
      name: 'Total Sensors',
      value: totalSensors,
      icon: Thermometer,
      color: 'bg-blue-500',
    },
    {
      name: 'Online Sensors',
      value: onlineSensors,
      icon: Activity,
      color: 'bg-green-500',
    },
    {
      name: 'Sensor Types',
      value: totalSensorTypes,
      icon: Database,
      color: 'bg-purple-500',
    },
    {
      name: 'Locations',
      value: totalLocations,
      icon: MapPin,
      color: 'bg-orange-500',
    },
  ];

  return (
    <div>
      <h1 className="text-2xl font-semibold text-gray-900 mb-6">Dashboard</h1>
      
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4 mb-8">
        {stats.map((stat) => {
          const Icon = stat.icon;
          return (
            <div key={stat.name} className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <div className={`${stat.color} rounded-md p-3`}>
                      <Icon className="h-6 w-6 text-white" />
                    </div>
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">
                        {stat.name}
                      </dt>
                      <dd>
                        <div className="text-lg font-medium text-gray-900">
                          {stat.value}
                        </div>
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
            Recent Sensors
          </h3>
          <div className="overflow-hidden">
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Name
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Type
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Location
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {sensorsData?.sensors?.slice(0, 5).map((sensor: any) => (
                    <tr key={sensor.id}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {sensor.name}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {sensor.sensorType.name}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {sensor.location.name}
                        {sensor.location.city && `, ${sensor.location.city}`}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                          sensor.isOnline 
                            ? 'bg-green-100 text-green-800' 
                            : 'bg-red-100 text-red-800'
                        }`}>
                          {sensor.isOnline ? 'Online' : 'Offline'}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;