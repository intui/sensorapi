import React from 'react';
import { X } from 'lucide-react';

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
  maxWidth?: 'sm' | 'md' | 'lg' | 'xl' | '2xl' | '3xl' | '4xl' | 'full';
}

const Modal: React.FC<ModalProps> = ({ isOpen, onClose, title, children, maxWidth = 'lg' }) => {
  if (!isOpen) return null;

  // Get the max width class - using full class names for Tailwind to detect them
  let maxWidthClass = 'max-w-lg'; // default
  if (maxWidth === 'sm') maxWidthClass = 'max-w-sm';
  else if (maxWidth === 'md') maxWidthClass = 'max-w-md';
  else if (maxWidth === 'xl') maxWidthClass = 'max-w-xl';
  else if (maxWidth === '2xl') maxWidthClass = 'max-w-2xl';
  else if (maxWidth === '3xl') maxWidthClass = 'max-w-3xl';
  else if (maxWidth === '4xl') maxWidthClass = 'max-w-4xl';
  else if (maxWidth === 'full') maxWidthClass = 'max-w-full';

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex items-center justify-center min-h-screen px-4 py-2">
        {/* Background overlay */}
        <div
          className="fixed inset-0 transition-opacity bg-gray-500 bg-opacity-75"
          onClick={onClose}
        />

        {/* Modal panel */}
        <div className={`relative z-10 inline-block w-full ${maxWidthClass} p-4 overflow-hidden text-left align-middle transition-all transform bg-white shadow-xl rounded-lg`}>
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-medium text-gray-900">
              {title}
            </h3>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 focus:outline-none focus:text-gray-600"
            >
              <X className="h-5 w-5" />
            </button>
          </div>

          {children}
        </div>
      </div>
    </div>
  );
};

export default Modal;
