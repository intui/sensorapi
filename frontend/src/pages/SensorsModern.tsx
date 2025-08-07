import React, { useState } from 'react';
import { useQuery, useMutation } from '@apollo/client';
import { GET_SENSORS, GET_SENSOR_TYPES, GET_LOCATIONS } from '../graphql/queries';
import { CREATE_SENSOR, UPDATE_SENSOR, DELETE_SENSOR } from '../graphql/mutations';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';
import Modal from '../components/Modal';
import ConfirmDialog from '../components/ConfirmDialog';
import { Plus, Edit, Trash2, Thermometer, Wifi, WifiOff, Database, Battery, Lightbulb, Zap } from 'lucide-react';
import type { Sensor, CreateSensorInput } from '../types';

const SensorsModern: React.FC = () => {
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
    onCompleted: () => {
      setShowForm(false);
      resetForm();
      refetch();
    },
    onError: (error) => {
      alert('Failed to create sensor: ' + error.message);
    },
  });

  const [updateSensor, { loading: updating }] = useMutation(UPDATE_SENSOR, {
    onCompleted: () => {
      setEditingItem(null);
      resetForm();
      refetch();
    },
    onError: (error) => {
      alert('Failed to update sensor: ' + error.message);
    },
  });

  const [deleteSensor, { loading: deleting }] = useMutation(DELETE_SENSOR, {
    onCompleted: () => {
      setDeleteItem(null);
      refetch();
    },
    onError: (error) => {
      alert('Failed to delete sensor: ' + error.message);
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
      samplingInterval: sensor.samplingInterval || undefined,
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
    
    try {
      if (editingItem) {
        await updateSensor({
          variables: {
            id: editingItem.id,
            input: formData,
          },
        });
      } else {
        await createSensor({
          variables: { input: formData },
        });
      }
    } catch (error) {
      console.error('Failed to save sensor:', error);
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

  const getSensorIcon = (type: string) => {
    switch(type.toLowerCase()) {
      case 'temperature': return <Thermometer size={20} />;
      case 'humidity': return <Database size={20} />;
      case 'pressure': return <Battery size={20} />;
      case 'light': return <Lightbulb size={20} />;
      case 'air quality': return <Zap size={20} />;
      default: return <Database size={20} />;
    }
  };

  const getStatusColor = (isOnline: boolean) => {
    return isOnline 
      ? 'bg-gradient-to-r from-cyan-500 to-blue-400' 
      : 'bg-gradient-to-r from-gray-500 to-gray-400';
  };

  if (loading) return <LoadingSpinner />;
  if (error) return <ErrorMessage message={error.message} />;

  const sensors: Sensor[] = data?.sensors || [];
  const sensorTypes = sensorTypesData?.sensorTypes || [];
  const locations = locationsData?.locations || [];

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-black p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-gradient-to-r from-cyan-400 to-blue-500 rounded-full flex items-center justify-center">
              <Thermometer className="text-white" size={24} />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white">Sensors</h1>
              <p className="text-gray-400">Manage your sensor devices</p>
            </div>
          </div>
          <button
            onClick={() => setShowForm(true)}
            disabled={creating}
            className="bg-gradient-to-r from-cyan-500 to-blue-500 hover:from-cyan-600 hover:to-blue-600 text-white px-6 py-3 rounded-xl font-medium transition-all flex items-center gap-2 shadow-lg"
          >
            <Plus size={20} />
            Add Sensor
          </button>
        </div>

        {/* Sensors Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {sensors.map((sensor: Sensor) => (
            <div
              key={sensor.id}
              className="bg-gray-800/30 backdrop-blur-sm rounded-2xl p-6 border border-gray-700/50 hover:bg-gray-800/50 transition-all"
            >
              {/* Sensor Header */}
              <div className="flex items-center justify-between mb-4">
                <div className={`w-12 h-12 rounded-full flex items-center justify-center ${getStatusColor(sensor.isOnline)}`}>
                  {getSensorIcon(sensor.sensorType.name)}
                </div>
                <div className="flex items-center gap-2">
                  {sensor.isOnline ? (
                    <Wifi className="text-cyan-400" size={16} />
                  ) : (
                    <WifiOff className="text-gray-400" size={16} />
                  )}
                  <span className={`text-sm font-medium ${
                    sensor.isOnline ? 'text-cyan-400' : 'text-gray-400'
                  }`}>
                    {sensor.isOnline ? 'Online' : 'Offline'}
                  </span>
                </div>
              </div>

              {/* Sensor Info */}
              <div className="mb-4">
                <h3 className="text-white font-bold text-lg mb-2">{sensor.name}</h3>
                <p className="text-gray-400 text-sm mb-3">{sensor.description}</p>
                
                <div className="space-y-2">
                  <div className="flex items-center gap-2">
                    <span className="text-xs px-2 py-1 bg-cyan-500/20 text-cyan-300 rounded-full">
                      {sensor.sensorType.name}
                    </span>
                    <span className="text-xs px-2 py-1 bg-blue-500/20 text-blue-300 rounded-full">
                      {sensor.location.name}
                    </span>
                  </div>
                  
                  <div className="text-gray-400 text-xs space-y-1">
                    <div>Device ID: {sensor.deviceId}</div>
                    {sensor.manufacturer && <div>Manufacturer: {sensor.manufacturer}</div>}
                    {sensor.model && <div>Model: {sensor.model}</div>}
                    {sensor.lastSeen && (
                      <div>Last seen: {new Date(sensor.lastSeen).toLocaleString()}</div>
                    )}
                  </div>
                </div>
              </div>

              {/* Actions */}
              <div className="flex gap-2">
                <button
                  onClick={() => handleEdit(sensor)}
                  className="flex-1 bg-gray-700/50 hover:bg-gray-600/50 text-gray-300 px-4 py-2 rounded-lg transition-all flex items-center justify-center gap-2"
                >
                  <Edit size={16} />
                  Edit
                </button>
                <button
                  onClick={() => setDeleteItem(sensor)}
                  className="flex-1 bg-red-500/20 hover:bg-red-500/30 text-red-300 px-4 py-2 rounded-lg transition-all flex items-center justify-center gap-2"
                >
                  <Trash2 size={16} />
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>

        {/* Modal and Dialogs */}
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
                  className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={creating || updating}
                  className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50"
                >
                  {creating || updating ? 'Saving...' : (editingItem ? 'Update' : 'Create')}
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
          isLoading={deleting}
        />
      </div>
    </div>
  );
};

export default SensorsModern;
