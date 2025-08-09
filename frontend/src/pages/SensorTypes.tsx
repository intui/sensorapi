import React, { useState } from 'react';
import { useQuery, useMutation } from '@apollo/client';
import { GET_SENSOR_TYPES } from '../graphql/queries';
import { CREATE_SENSOR_TYPE, UPDATE_SENSOR_TYPE, DELETE_SENSOR_TYPE } from '../graphql/mutations';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';
import Modal from '../components/Modal';
import ConfirmDialog from '../components/ConfirmDialog';
import { Plus, Edit, Trash2 } from 'lucide-react';
import type { SensorType, CreateSensorTypeInput } from '../types';

const SensorTypes: React.FC = () => {
  const [showForm, setShowForm] = useState(false);
  const [editingItem, setEditingItem] = useState<SensorType | null>(null);
  const [deleteItem, setDeleteItem] = useState<SensorType | null>(null);
  const [formData, setFormData] = useState<CreateSensorTypeInput>({
    name: '',
    description: '',
    unit: '',
    minValue: undefined,
    maxValue: undefined,
  });

  const { data, loading, error, refetch } = useQuery(GET_SENSOR_TYPES);
  
  const [createSensorType, { loading: creating }] = useMutation(CREATE_SENSOR_TYPE, {
    onCompleted: () => {
      setShowForm(false);
      resetForm();
      refetch();
    },
  });

  const [updateSensorType, { loading: updating }] = useMutation(UPDATE_SENSOR_TYPE, {
    onCompleted: () => {
      setEditingItem(null);
      resetForm();
      refetch();
    },
  });

  const [deleteSensorType] = useMutation(DELETE_SENSOR_TYPE, {
    onCompleted: () => {
      setDeleteItem(null);
      refetch();
    },
  });

  const resetForm = () => {
    setFormData({
      name: '',
      description: '',
      unit: '',
      minValue: undefined,
      maxValue: undefined,
    });
  };

  const handleEdit = (sensorType: SensorType) => {
    setFormData({
      name: sensorType.name,
      description: sensorType.description || '',
      unit: sensorType.unit || '',
      minValue: sensorType.minValue,
      maxValue: sensorType.maxValue,
    });
    setEditingItem(sensorType);
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
        // Update existing sensor type
        await updateSensorType({
          variables: {
            id: editingItem.id,
            input: {
              name: formData.name,
              description: formData.description || null,
              unit: formData.unit || null,
              minValue: formData.minValue || null,
              maxValue: formData.maxValue || null,
            },
          },
        });
      } else {
        // Create new sensor type
        await createSensorType({
          variables: {
            input: {
              ...formData,
              minValue: formData.minValue || null,
              maxValue: formData.maxValue || null,
            },
          },
        });
      }
    } catch (error) {
      console.error('Failed to save sensor type:', error);
    }
  };

  const handleDelete = async () => {
    if (deleteItem) {
      try {
        await deleteSensorType({
          variables: { id: deleteItem.id },
        });
      } catch (error) {
        console.error('Failed to delete sensor type:', error);
      }
    }
  };

  if (loading) return <LoadingSpinner />;
  if (error) return <ErrorMessage message={error.message} />;

  const sensorTypes: SensorType[] = data?.sensorTypes || [];

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-semibold text-gray-900">Sensor Types</h1>
        <button
          onClick={() => setShowForm(!showForm)}
          className="btn btn-primary"
        >
          <Plus className="h-4 w-4 mr-2" />
          Add Sensor Type
        </button>
      </div>

      {(showForm || editingItem) && (
        <Modal 
          isOpen={showForm || !!editingItem} 
          onClose={handleCloseModal}
          title={editingItem ? 'Edit Sensor Type' : 'Create New Sensor Type'}
        >
          <form onSubmit={handleSubmit}>
            <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
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
                <label className="block text-sm font-medium text-gray-700">Unit</label>
                <input
                  type="text"
                  value={formData.unit}
                  onChange={(e) => setFormData({ ...formData, unit: e.target.value })}
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                  placeholder="e.g., °C, %, Pa"
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
              <div>
                <label className="block text-sm font-medium text-gray-700">Min Value</label>
                <input
                  type="number"
                  step="any"
                  value={formData.minValue || ''}
                  onChange={(e) => setFormData({ ...formData, minValue: e.target.value ? parseFloat(e.target.value) : undefined })}
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Max Value</label>
                <input
                  type="number"
                  step="any"
                  value={formData.maxValue || ''}
                  onChange={(e) => setFormData({ ...formData, maxValue: e.target.value ? parseFloat(e.target.value) : undefined })}
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
        title="Delete Sensor Type"
        message={`Are you sure you want to delete "${deleteItem?.name}"? This action cannot be undone.`}
        confirmText="Delete"
        isDestructive={true}
      />

      <div className="bg-white shadow rounded-lg">
        <div className="overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Name
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Description
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Unit
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Range
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {sensorTypes.map((sensorType) => (
                <tr key={sensorType.id}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {sensorType.name}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500">
                    {sensorType.description || '-'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {sensorType.unit || '-'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {sensorType.minValue !== null && sensorType.maxValue !== null
                      ? `${sensorType.minValue} - ${sensorType.maxValue}`
                      : sensorType.minValue !== null
                      ? `≥ ${sensorType.minValue}`
                      : sensorType.maxValue !== null
                      ? `≤ ${sensorType.maxValue}`
                      : '-'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <button 
                      onClick={() => handleEdit(sensorType)}
                      className="text-blue-600 hover:text-blue-900 mr-3"
                      title="Edit sensor type"
                    >
                      <Edit className="h-4 w-4" />
                    </button>
                    <button 
                      onClick={() => setDeleteItem(sensorType)}
                      className="text-red-600 hover:text-red-900"
                      title="Delete sensor type"
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

export default SensorTypes;