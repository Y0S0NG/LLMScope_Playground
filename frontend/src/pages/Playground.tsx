import { useState } from 'react';
import { ChatPanel } from '../components/ChatPanel';
import { MetricsPanel } from '../components/MetricsPanel';
import { EventHistory } from '../components/EventHistory';
import { Navbar } from '../components/Navbar';

export const Playground = () => {
  const [rightView, setRightView] = useState<'metrics' | 'events'>('metrics');

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col">
      <Navbar />

      <div className="flex-1 flex overflow-hidden">
        {/* Chat Panel (Left) */}
        <div className="w-1/2 bg-white border-r border-gray-200">
          <ChatPanel />
        </div>

        {/* Right Panel with Toggle */}
        <div className="w-1/2 bg-white flex flex-col">
          {/* Toggle Tabs */}
          <div className="flex border-b border-gray-200 bg-white">
            <button
              onClick={() => setRightView('metrics')}
              className={`flex-1 px-6 py-4 text-sm font-semibold transition ${
                rightView === 'metrics'
                  ? 'text-indigo-600 border-b-2 border-indigo-600 bg-indigo-50'
                  : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'
              }`}
            >
              Metrics
            </button>
            <button
              onClick={() => setRightView('events')}
              className={`flex-1 px-6 py-4 text-sm font-semibold transition ${
                rightView === 'events'
                  ? 'text-indigo-600 border-b-2 border-indigo-600 bg-indigo-50'
                  : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'
              }`}
            >
              Event History
            </button>
          </div>

          {/* Content */}
          <div className="flex-1 overflow-hidden">
            {rightView === 'metrics' ? <MetricsPanel /> : <EventHistory />}
          </div>
        </div>
      </div>
    </div>
  );
};
