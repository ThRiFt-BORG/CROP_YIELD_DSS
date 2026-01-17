import { useYieldStore } from '../store/yieldStore';
import TimeSeriesChart from './TimeSeriesChart';

export default function AnalysisPanel() {
  const { data, loading, error } = useYieldStore();

  if (loading) {
    return (
      <div className="text-center p-4">
        <p className="text-blue-500">Loading analysis data...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center p-4 bg-red-100 border border-red-400 text-red-700">
        <p>Error: {error}</p>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="text-center p-4 text-gray-500">
        <h2 className="text-xl font-bold mb-4">Crop Yield DSS</h2>
        <p>Click on the map to analyze a location.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-green-700 border-b pb-2">Analysis Results</h2>

      {/* Predicted Yield */}
      <div className="bg-green-100 p-4 rounded-lg shadow-md">
        <p className="text-sm font-medium text-green-800">Predicted Yield (Units/Acre)</p>
        <p className="text-4xl font-extrabold text-green-600">
          {data.predicted_yield.toFixed(2)}
        </p>
      </div>

      {/* Time Series Chart */}
      <div>
        <h3 className="text-lg font-semibold mb-2">NDVI Time Series</h3>
        <TimeSeriesChart data={data.time_series} />
      </div>

      {/* Features Used */}
      <div>
        <h3 className="text-lg font-semibold mb-2">Features Used for Prediction</h3>
        <ul className="space-y-1 text-sm">
          {data.features.map((feature, index) => (
            <li key={index} className="flex justify-between border-b border-gray-200 pb-1">
              <span className="font-medium capitalize">{feature.name.replace('_', ' ')}:</span>
              <span className="text-gray-600">{feature.value.toFixed(2)}</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
