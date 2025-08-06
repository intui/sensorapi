import React, { useState } from 'react';
import { useQuery, useMutation } from '@apollo/client';
import { GET_SENSORS, GET_SENSOR_TYPES, GET_LOCATIONS } from '../graphql/queries';
import { CREATE_SENSOR, UPDATE_SENSOR, DELETE_SENSOR } from '../graphql/mutations';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';
import Modal from '../components/Modal';
import ConfirmDialog from '../components/ConfirmDialog';
import { Plus, Edit, Trash2, Thermometer, Wifi, WifiOff } from 'lucide-react';
import type { Sensor, CreateSensorInput } from '../types';

const Sensors: React.FC = () => {
  const [showForm, setShowForm] = useState(false);
  const [editingItem, setEditingItem] = useState<Sensor | null>(null);
  const [deleteItem, setDeleteItem] = useState<Sensor | null>(null);
  const [formData, setFormData] = useState<CreateSensorInput>({
    deviceId: '',
    name: '',
    description: '',
    sensorTypeId: '',
    locationId: '',
    manufacturer: '',
    model: '',
    firmwareVersion: '',
    hardwareVersion: '',
    samplingInterval: undefined,
  });

  const { data, loading, error, refetch } = useQuery(GET_SENSORS);
  const { data: sensorTypesData } = useQuery(GET_SENSOR_TYPES);
  const { data: locationsData } = useQuery(GET_LOCATIONS);
  
  const [createSensor, { loading: creating }] = useMutation(CREATE_SENSOR, {
    onCompleted: (data) => {
      console.log('Create mutation completed:', data);
      setShowForm(false);
      resetForm();
      refetch();
    },
    onError: (error) => {
      console.error('Create mutation error:', error);
      alert('Failed to create sensor: ' + error.message);
    },
  });

  const [updateSensor, { loading: updating }] = useMutation(UPDATE_SENSOR, {
    onCompleted: (data) => {
      console.log('Update mutation completed:', data);
      setEditingItem(null);
      resetForm();
      refetch();
    },
    onError: (error) => {
      console.error('Update mutation error:', error);
      alert('Failed to update sensor: ' + error.message);
    },
  });

  const [deleteSensor, { loading: deleting }] = useMutation(DELETE_SENSOR, {
    onCompleted: () => {
      setDeleteItem(null);
      refetch();
    },
  });

  const resetForm = () => {
    setFormData({
      deviceId: '',
      name: '',
      description: '',
      sensorTypeId: '',
      locationId: '',
      manufacturer: '',
      model: '',
      firmwareVersion: '',
      hardwareVersion: '',
      samplingInterval: undefined,
    });
  };

  const handleEdit = (sensor: Sensor) => {
    console.log('Editing sensor:', sensor);
    setFormData({
      deviceId: sensor.deviceId,
      name: sensor.name,
      description: sensor.description || '',
      sensorTypeId: sensor.sensorType.id,
      locationId: sensor.location.id,
      manufacturer: sensor.manufacturer || '',
      model: sensor.model || '',
      firmwareVersion: sensor.firmwareVersion || '',
      hardwareVersion: sensor.hardwareVersion || '',
      samplingInterval: sensor.samplingInterval,
    });
    console.log('Form data set:', {
      deviceId: sensor.deviceId,
      name: sensor.name,
      description: sensor.description || '',
      sensorTypeId: sensor.sensorType.id,
      locationId: sensor.location.id,
      manufacturer: sensor.manufacturer || '',
      model: sensor.model || '',
      firmwareVersion: sensor.firmwareVersion || '',
      hardwareVersion: sensor.hardwareVersion || '',
      samplingInterval: sensor.samplingInterval,
    });
    setEditingItem(sensor);
  };

  const handleCloseModal = () => {
    setShowForm(false);
    setEditingItem(null);
    resetForm();
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    console.log('Submitting form:', { editingItem: !!editingItem, formData });
    
    try {
      if (editingItem) {
        // Update existing sensor
        console.log('Updating sensor with ID:', editingItem.id);
        const updateVariables = {
          id: editingItem.id,
          input: {
            deviceId: formData.deviceId,
            name: formData.name,
            description: formData.description || null,
            sensorTypeId: formData.sensorTypeId,
            locationId: formData.locationId,
            manufacturer: formData.manufacturer || null,
            model: formData.model || null,
            firmwareVersion: formData.firmwareVersion || null,
            hardwareVersion: formData.hardwareVersion || null,
            samplingInterval: formData.samplingInterval || null,
          },
        };
        console.log('Update variables:', updateVariables);
        const result = await updateSensor({
          variables: updateVariables,
        });
        console.log('Update result:', result);
      } else {
        // Create new sensor
        console.log('Creating new sensor');
        const result = await createSensor({
          variables: {
            input: {
              ...formData,
              description: formData.description || null,
              manufacturer: formData.manufacturer || null,
              model: formData.model || null,
              firmwareVersion: formData.firmwareVersion || null,
              hardwareVersion: formData.hardwareVersion || null,
              samplingInterval: formData.samplingInterval || null,
            },
          },
        });
        console.log('Create result:', result);
      }
    } catch (error) {
      console.error('Failed to save sensor:', error);
      // Error is already handled by the mutation's onError callback
    }
  };

  const handleDelete = async () => {
    if (deleteItem) {
      try {
        await deleteSensor({
          variables: { id: deleteItem.id },
        });
      } catch (error) {
        console.error('Failed to delete sensor:', error);
      }
    }
  };

  if (loading) return <LoadingSpinner />;
  if (error) return <ErrorMessage message={error.message} />;

  const sensors: Sensor[] = data?.sensors || [];
  const sensorTypes = sensorTypesData?.sensorTypes || [];
  const locations = locationsData?.locations || [];

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-semibold text-gray-900">Sensors</h1>
        <button
          onClick={() => setShowForm(!showForm)}
          className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700"
        >
          <Plus className="h-4 w-4 mr-2" />
          Add Sensor
        </button>
      </div>

      {(showForm || editingItem) && (
        <Modal 
          isOpen={showForm || !!editingItem} 
          onClose={handleCloseModal}
          title={editingItem ? 'Edit Sensor' : 'Create New Sensor'}
        >
          <form onSubmit={handleSubmit}>
            <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
              <div>
                <label className="block text-sm font-medium text-gray-700">Device ID *</label>
                <input
                  type="text"
                  required
                  value={formData.deviceId}
                  onChange={(e) => setFormData({ ...formData, deviceId: e.target.value })}
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Name *</label>
                <input
                  type="text"
                  required
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Sensor Type *</label>
                <select
                  required
                  value={formData.sensorTypeId}
                  onChange={(e) => setFormData({ ...formData, sensorTypeId: e.target.value })}
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="">Select a sensor type</option>
                  {sensorTypes.map((type: any) => (
                    <option key={type.id} value={type.id}>
                      {type.name} {type.unit ? `(${type.unit})` : ''}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Location *</label>
                <select
                  required
                  value={formData.locationId}
                  onChange={(e) => setFormData({ ...formData, locationId: e.target.value })}
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="">Select a location</option>
                  {locations.map((location: any) => (
                    <option key={location.id} value={location.id}>
                      {location.name} {location.city ? `(${location.city})` : ''}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Manufacturer</label>
                <input
                  type="text"
                  value={formData.manufacturer}
                  onChange={(e) => setFormData({ ...formData, manufacturer: e.target.value })}
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Model</label>
                <input
                  type="text"
                  value={formData.model}
                  onChange={(e) => setFormData({ ...formData, model: e.target.value })}
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Sampling Interval (seconds)</label>
                <input
                  type="number"
                  value={formData.samplingInterval || ''}
                  onChange={(e) => setFormData({ ...formData, samplingInterval: e.target.value ? parseInt(e.target.value) : undefined })}
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              <div className="sm:col-span-2">
                <label className="block text-sm font-medium text-gray-700">Description</label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  rows={3}
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
            </div>
            <div className="mt-6 flex justify-end space-x-3">
              <button
                type="button"
                onClick={handleCloseModal}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={creating || updating}
                className="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
              >
                {creating || updating ? (editingItem ? 'Updating...' : 'Creating...') : (editingItem ? 'Update' : 'Create')}
              </button>
            </div>
          </form>
        </Modal>
      )}

      <ConfirmDialog
        isOpen={!!deleteItem}
        onClose={() => setDeleteItem(null)}
        onConfirm={handleDelete}
        title="Delete Sensor"
        message={`Are you sure you want to delete "${deleteItem?.name}"? This action cannot be undone and will also delete all associated sensor readings.`}
        confirmText="Delete"
        isDestructive={true}
      />

      <div className="bg-white shadow rounded-lg">
        <div className="overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Sensor
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
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Last Seen
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {sensors.map((sensor) => (
                <tr key={sensor.id}>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <Thermometer className="h-4 w-4 text-gray-400 mr-3" />
                      <div>
                        <div className="text-sm font-medium text-gray-900">
                          {sensor.name}
                        </div>
                        <div className="text-sm text-gray-500">
                          {sensor.deviceId}
                        </div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {sensor.sensorType.name}
                    {sensor.sensorType.unit && (
                      <span className="text-gray-400"> ({sensor.sensorType.unit})</span>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {sensor.location.name}
                    {sensor.location.city && (
                      <div className="text-xs text-gray-400">{sensor.location.city}</div>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      {sensor.isOnline ? (
                        <Wifi className="h-4 w-4 text-green-500 mr-2" />
                      ) : (
                        <WifiOff className="h-4 w-4 text-red-500 mr-2" />
                      )}
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                        sensor.isOnline 
                          ? 'bg-green-100 text-green-800' 
                          : 'bg-red-100 text-red-800'
                      }`}>
                        {sensor.isOnline ? 'Online' : 'Offline'}
                      </span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {sensor.lastSeen 
                      ? new Date(sensor.lastSeen).toLocaleString()
                      : 'Never'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <button 
                      onClick={() => handleEdit(sensor)}
                      className="text-blue-600 hover:text-blue-900 mr-3"
                      title="Edit sensor"
                    >
                      <Edit className="h-4 w-4" />
                    </button>
                    <button 
                      onClick={() => setDeleteItem(sensor)}
                      className="text-red-600 hover:text-red-900"
                      title="Delete sensor"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default Sensors;