import React from 'react';
import { TimeSeriesData } from '../types/api';

interface TimeSeriesChartProps {
  data: TimeSeriesData[];
}

// Simple bar chart implementation using Tailwind CSS for visualization
const TimeSeriesChart: React.FC<TimeSeriesChartProps> = ({ data }) => {
  if (!data || data.length === 0) {
    return <div className="text-gray-500 text-sm">No time series data available.</div>;
  }

  const maxVal = Math.max(...data.map(d => d.value));
  const minVal = Math.min(...data.map(d => d.value));
  const range = maxVal - minVal;

  return (
    <div className="flex flex-col space-y-2 p-2 border rounded-lg bg-white">
      <div className="flex justify-between text-xs text-gray-500 px-1">
        <span>{maxVal.toFixed(2)}</span>
        <span>NDVI</span>
      </div>
      <div className="flex h-24 items-end space-x-1">
        {data.map((d, index) => {
          // Normalize value to 0-100% height
          const normalizedHeight = range > 0 ? ((d.value - minVal) / range) * 80 + 20 : 50; // Min height 20%
          const dateLabel = new Date(d.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' });

          return (
            <div key={index} className="flex flex-col items-center flex-grow group relative">
              <div
                className="w-full bg-blue-500 hover:bg-blue-700 transition-colors rounded-t-sm"
                style={{ height: `${normalizedHeight}%` }}
              ></div>
              <span className="text-xs mt-1 text-gray-600">{dateLabel}</span>
              <div className="absolute bottom-full mb-2 hidden group-hover:block bg-gray-800 text-white text-xs p-1 rounded">
                {d.value.toFixed(3)}
              </div>
            </div>
          );
        })}
      </div>
      <div className="flex justify-between text-xs text-gray-500 px-1">
        <span>{minVal.toFixed(2)}</span>
        <span>Date</span>
      </div>
    </div>
  );
};

export default TimeSeriesChart;
