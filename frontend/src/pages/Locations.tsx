import React, { useState } from 'react';
import { useQuery, useMutation } from '@apollo/client';
import { GET_LOCATIONS } from '../graphql/queries';
import { CREATE_LOCATION, UPDATE_LOCATION, DELETE_LOCATION } from '../graphql/mutations';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';
import Modal from '../components/Modal';
import ConfirmDialog from '../components/ConfirmDialog';
import { Plus, Edit, Trash2, MapPin } from 'lucide-react';
import type { Location, CreateLocationInput } from '../types';

const Locations: React.FC = () => {
  const [showForm, setShowForm] = useState(false);
  const [editingItem, setEditingItem] = useState<Location | null>(null);
  const [deleteItem, setDeleteItem] = useState<Location | null>(null);
  const [formData, setFormData] = useState<CreateLocationInput>({
    name: '',
    description: '',
    city: '',
    country: '',
    postalCode: '',
    address: '',
    latitude: undefined,
    longitude: undefined,
  });

  const { data, loading, error, refetch } = useQuery(GET_LOCATIONS);
  
  const [createLocation, { loading: creating }] = useMutation(CREATE_LOCATION, {
    onCompleted: () => {
      setShowForm(false);
      resetForm();
      refetch();
    },
  });

  const [updateLocation, { loading: updating }] = useMutation(UPDATE_LOCATION, {
    onCompleted: () => {
      setEditingItem(null);
      resetForm();
      refetch();
    },
  });

  const [deleteLocation, { loading: deleting }] = useMutation(DELETE_LOCATION, {
    onCompleted: () => {
      setDeleteItem(null);
      refetch();
    },
  });

  const resetForm = () => {
    setFormData({
      name: '',
      description: '',
      city: '',
      country: '',
      postalCode: '',
      address: '',
      latitude: undefined,
      longitude: undefined,
    });
  };

  const handleEdit = (location: Location) => {
    setFormData({
      name: location.name,
      description: location.description || '',
      city: location.city || '',
      country: location.country || '',
      postalCode: location.postalCode || '',
      address: location.address || '',
      latitude: location.latitude,
      longitude: location.longitude,
    });
    setEditingItem(location);
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
        // Update existing location
        await updateLocation({
          variables: {
            id: editingItem.id,
            input: {
              name: formData.name,
              description: formData.description || null,
              city: formData.city || null,
              country: formData.country || null,
              postalCode: formData.postalCode || null,
              address: formData.address || null,
              latitude: formData.latitude || null,
              longitude: formData.longitude || null,
            },
          },
        });
      } else {
        // Create new location
        await createLocation({
          variables: {
            input: {
              ...formData,
              latitude: formData.latitude || null,
              longitude: formData.longitude || null,
            },
          },
        });
      }
    } catch (error) {
      console.error('Failed to save location:', error);
    }
  };

  const handleDelete = async () => {
    if (deleteItem) {
      try {
        await deleteLocation({
          variables: { id: deleteItem.id },
        });
      } catch (error) {
        console.error('Failed to delete location:', error);
      }
    }
  };

  if (loading) return <LoadingSpinner />;
  if (error) return <ErrorMessage message={error.message} />;

  const locations: Location[] = data?.locations || [];

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-semibold text-gray-900">Locations</h1>
        <button
          onClick={() => setShowForm(!showForm)}
          className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700"
        >
          <Plus className="h-4 w-4 mr-2" />
          Add Location
        </button>
      </div>

      {(showForm || editingItem) && (
        <Modal 
          isOpen={showForm || !!editingItem} 
          onClose={handleCloseModal}
          title={editingItem ? 'Edit Location' : 'Create New Location'}
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
                <label className="block text-sm font-medium text-gray-700">City</label>
                <input
                  type="text"
                  value={formData.city}
                  onChange={(e) => setFormData({ ...formData, city: e.target.value })}
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Country</label>
                <input
                  type="text"
                  value={formData.country}
                  onChange={(e) => setFormData({ ...formData, country: e.target.value })}
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Postal Code</label>
                <input
                  type="text"
                  value={formData.postalCode}
                  onChange={(e) => setFormData({ ...formData, postalCode: e.target.value })}
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              <div className="sm:col-span-2">
                <label className="block text-sm font-medium text-gray-700">Address</label>
                <input
                  type="text"
                  value={formData.address}
                  onChange={(e) => setFormData({ ...formData, address: e.target.value })}
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
              <div>
                <label className="block text-sm font-medium text-gray-700">Latitude</label>
                <input
                  type="number"
                  step="any"
                  value={formData.latitude || ''}
                  onChange={(e) => setFormData({ ...formData, latitude: e.target.value ? parseFloat(e.target.value) : undefined })}
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Longitude</label>
                <input
                  type="number"
                  step="any"
                  value={formData.longitude || ''}
                  onChange={(e) => setFormData({ ...formData, longitude: e.target.value ? parseFloat(e.target.value) : undefined })}
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
        title="Delete Location"
        message={`Are you sure you want to delete "${deleteItem?.name}"? This action cannot be undone and may affect associated sensors.`}
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
                  Address
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  City/Country
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Coordinates
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {locations.map((location) => (
                <tr key={location.id}>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <MapPin className="h-4 w-4 text-gray-400 mr-2" />
                      <div>
                        <div className="text-sm font-medium text-gray-900">
                          {location.name}
                        </div>
                        {location.description && (
                          <div className="text-sm text-gray-500">
                            {location.description}
                          </div>
                        )}
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500">
                    {location.address || '-'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {[location.city, location.country].filter(Boolean).join(', ') || '-'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {location.latitude && location.longitude
                      ? `${location.latitude.toFixed(4)}, ${location.longitude.toFixed(4)}`
                      : '-'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                      location.isActive 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-red-100 text-red-800'
                    }`}>
                      {location.isActive ? 'Active' : 'Inactive'}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <button 
                      onClick={() => handleEdit(location)}
                      className="text-blue-600 hover:text-blue-900 mr-3"
                      title="Edit location"
                    >
                      <Edit className="h-4 w-4" />
                    </button>
                    <button 
                      onClick={() => setDeleteItem(location)}
                      className="text-red-600 hover:text-red-900"
                      title="Delete location"
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

export default Locations;