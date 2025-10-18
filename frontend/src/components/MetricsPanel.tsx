import { useSession } from '../contexts/SessionContext';
import { useEffect, useState } from 'react';
import { getRecentEvents } from '../api/client';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import type { EventResponse } from '../types';

interface ChartDataPoint {
  time: string;
  tokens: number;
  timestamp: number;
}

type TimeGranularity = 'minute' | 'hour' | 'day';

export const MetricsPanel = () => {
  const { metrics, sessionInfo, refreshMetrics, isLoading } = useSession();
  const [events, setEvents] = useState<EventResponse[]>([]);
  const [chartData, setChartData] = useState<ChartDataPoint[]>([]);
  const [timeGranularity, setTimeGranularity] = useState<TimeGranularity>('minute');

  // Auto-refresh metrics and events every 5 seconds
  useEffect(() => {
    const loadData = async () => {
      try {
        const eventData = await getRecentEvents(100);
        setEvents(eventData);
        processChartData(eventData, timeGranularity);
      } catch (error) {
        console.error('Failed to load events:', error);
      }
    };

    loadData();
    refreshMetrics();

    const interval = setInterval(() => {
      loadData();
      refreshMetrics();
    }, 5000);

    return () => clearInterval(interval);
  }, [refreshMetrics, timeGranularity]);

  const processChartData = (eventData: EventResponse[], granularity: TimeGranularity) => {
    if (!eventData || eventData.length === 0) {
      setChartData([]);
      return;
    }

    // Group by time unit and sum tokens
    const timeData = new Map<string, { tokens: number; timestamp: number }>();

    eventData.forEach((event) => {
      const eventDate = new Date(event.time);
      let timeKey: string;

      // Create time key based on granularity
      switch (granularity) {
        case 'minute':
          timeKey = new Date(
            eventDate.getFullYear(),
            eventDate.getMonth(),
            eventDate.getDate(),
            eventDate.getHours(),
            eventDate.getMinutes()
          ).toISOString();
          break;
        case 'hour':
          timeKey = new Date(
            eventDate.getFullYear(),
            eventDate.getMonth(),
            eventDate.getDate(),
            eventDate.getHours()
          ).toISOString();
          break;
        case 'day':
          timeKey = new Date(
            eventDate.getFullYear(),
            eventDate.getMonth(),
            eventDate.getDate()
          ).toISOString();
          break;
      }

      const existing = timeData.get(timeKey) || { tokens: 0, timestamp: new Date(timeKey).getTime() };
      existing.tokens += (event.tokens_prompt || 0) + (event.tokens_completion || 0);
      timeData.set(timeKey, existing);
    });

    // Convert to array and sort by time
    const chartPoints: ChartDataPoint[] = Array.from(timeData.entries())
      .map(([time, data]) => {
        const date = new Date(time);
        let formattedTime: string;

        // Format time label based on granularity
        switch (granularity) {
          case 'minute':
            formattedTime = date.toLocaleTimeString('en-US', {
              hour: '2-digit',
              minute: '2-digit',
              hour12: false
            });
            break;
          case 'hour':
            formattedTime = date.toLocaleTimeString('en-US', {
              month: 'short',
              day: 'numeric',
              hour: '2-digit',
              hour12: false
            });
            break;
          case 'day':
            formattedTime = date.toLocaleDateString('en-US', {
              month: 'short',
              day: 'numeric'
            });
            break;
        }

        return {
          time: formattedTime,
          tokens: data.tokens,
          timestamp: data.timestamp
        };
      })
      .sort((a, b) => a.timestamp - b.timestamp);

    setChartData(chartPoints);
  };

  // Calculate recent metrics
  const recentEvents = events.slice(0, 10);
  const avgLatency = recentEvents.length > 0
    ? recentEvents.reduce((sum, e) => sum + (e.latency_ms || 0), 0) / recentEvents.length
    : 0;

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-gray-500">Loading metrics...</div>
      </div>
    );
  }

  return (
    <div className="h-full overflow-y-auto p-6 space-y-6 bg-gradient-to-br from-gray-50 to-blue-50">
      <div>
        <h2 className="text-2xl font-bold text-gray-800 mb-1">Live Dashboard</h2>
        <p className="text-sm text-gray-500">Session metrics with real-time updates</p>
      </div>

      {/* Metrics Cards Grid */}
      <div className="grid grid-cols-2 gap-4">
        {/* Total Events */}
        <div className="bg-gradient-to-br from-blue-500/10 to-blue-600/10 p-4 rounded-lg border border-blue-200">
          <div className="text-xs text-blue-700 font-semibold mb-1 uppercase tracking-wide">Total Events</div>
          <div className="text-3xl font-bold text-blue-900">
            {metrics?.event_count || 0}
          </div>
        </div>

        {/* Total Tokens */}
        <div className="bg-gradient-to-br from-purple-500/10 to-purple-600/10 p-4 rounded-lg border border-purple-200">
          <div className="text-xs text-purple-700 font-semibold mb-1 uppercase tracking-wide">Total Tokens</div>
          <div className="text-3xl font-bold text-purple-900">
            {(metrics?.total_tokens || 0).toLocaleString()}
          </div>
        </div>

        {/* Total Cost */}
        <div className="bg-gradient-to-br from-green-500/10 to-green-600/10 p-4 rounded-lg border border-green-200">
          <div className="text-xs text-green-700 font-semibold mb-1 uppercase tracking-wide">Total Cost</div>
          <div className="text-3xl font-bold text-green-900">
            ${(metrics?.total_cost || 0).toFixed(4)}
          </div>
        </div>

        {/* Average Latency */}
        <div className="bg-gradient-to-br from-orange-500/10 to-orange-600/10 p-4 rounded-lg border border-orange-200">
          <div className="text-xs text-orange-700 font-semibold mb-1 uppercase tracking-wide">Avg Latency</div>
          <div className="text-3xl font-bold text-orange-900">
            {avgLatency.toFixed(0)}ms
          </div>
          <div className="text-xs text-orange-600 mt-1">Last 10 events</div>
        </div>
      </div>

      {/* Token Usage Chart */}
      <div className="bg-white p-5 rounded-lg border border-gray-200 shadow-sm">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-800">Token Usage Over Time</h3>
          <div className="flex items-center gap-2">
            <span className="text-xs text-gray-500">Granularity:</span>
            <select
              value={timeGranularity}
              onChange={(e) => setTimeGranularity(e.target.value as TimeGranularity)}
              className="bg-white border border-gray-300 text-gray-700 text-xs rounded-lg px-2 py-1 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none"
            >
              <option value="minute">Minute</option>
              <option value="hour">Hour</option>
              <option value="day">Day</option>
            </select>
          </div>
        </div>

        {chartData.length === 0 ? (
          <div className="h-48 flex items-center justify-center text-gray-400">
            <div className="text-center">
              <p className="text-sm mb-1">No data yet</p>
              <p className="text-xs">Start chatting to see the chart</p>
            </div>
          </div>
        ) : (
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
              <XAxis
                dataKey="time"
                stroke="#6B7280"
                style={{ fontSize: '11px' }}
                angle={timeGranularity === 'minute' ? -45 : 0}
                textAnchor={timeGranularity === 'minute' ? 'end' : 'middle'}
                height={timeGranularity === 'minute' ? 60 : 40}
              />
              <YAxis
                stroke="#6B7280"
                style={{ fontSize: '11px' }}
                label={{ value: 'Tokens', angle: -90, position: 'insideLeft', style: { fill: '#6B7280', fontSize: '11px' } }}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#FFFFFF',
                  border: '1px solid #E5E7EB',
                  borderRadius: '6px',
                  fontSize: '12px'
                }}
              />
              <Legend wrapperStyle={{ fontSize: '12px' }} />
              <Line
                type="monotone"
                dataKey="tokens"
                stroke="#6366F1"
                strokeWidth={2}
                dot={{ fill: '#6366F1', r: 3 }}
                activeDot={{ r: 5 }}
                name="Tokens Used"
              />
            </LineChart>
          </ResponsiveContainer>
        )}
      </div>

      {/* Models Used */}
      {metrics && metrics.models_used.length > 0 && (
        <div className="bg-white p-5 rounded-lg border border-gray-200 shadow-sm">
          <div className="text-sm text-gray-700 font-semibold mb-3">Models Used</div>
          <div className="flex flex-wrap gap-2">
            {metrics.models_used.map((model, idx) => (
              <span
                key={idx}
                className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-indigo-100 text-indigo-800"
              >
                {model}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Session Info */}
      {sessionInfo && (
        <div className="bg-white p-5 rounded-lg border border-gray-200 shadow-sm">
          <div className="text-sm text-gray-700 font-semibold mb-3">Session Info</div>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between items-center py-1">
              <span className="text-gray-500">Created:</span>
              <span className="text-gray-800 font-medium">
                {new Date(sessionInfo.created_at).toLocaleString()}
              </span>
            </div>
            <div className="flex justify-between items-center py-1">
              <span className="text-gray-500">Last Active:</span>
              <span className="text-gray-800 font-medium">
                {new Date(sessionInfo.last_activity).toLocaleString()}
              </span>
            </div>
            <div className="flex justify-between items-center py-1">
              <span className="text-gray-500">Status:</span>
              <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-semibold ${
                sessionInfo.is_active
                  ? 'bg-green-100 text-green-800'
                  : 'bg-red-100 text-red-800'
              }`}>
                {sessionInfo.is_active ? '● Active' : '○ Inactive'}
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Recent Events Summary */}
      {recentEvents.length > 0 && (
        <div className="bg-white p-5 rounded-lg border border-gray-200 shadow-sm">
          <div className="text-sm text-gray-700 font-semibold mb-3">Recent Activity</div>
          <div className="space-y-2">
            {recentEvents.slice(0, 5).map((event, idx) => (
              <div key={idx} className="flex justify-between items-center text-xs py-2 border-b border-gray-100 last:border-0">
                <div className="flex items-center gap-2">
                  <span className="text-gray-500">
                    {new Date(event.time).toLocaleTimeString()}
                  </span>
                  <span className="text-gray-700 font-mono">{event.model}</span>
                </div>
                <div className="flex items-center gap-3">
                  <span className="text-gray-600">{((event.tokens_prompt || 0) + (event.tokens_completion || 0)).toLocaleString()} tokens</span>
                  <span className="text-gray-500">{event.latency_ms}ms</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
