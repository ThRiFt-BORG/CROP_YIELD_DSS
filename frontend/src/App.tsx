import MapView from './components/MapView';
import AnalysisPanel from './components/AnalysisPanel';

function App() {
  return (
    <div className="flex h-screen w-screen">
      {/* Map View - Takes up most of the screen */}
      <div className="flex-grow">
        <MapView />
      </div>
      
      {/* Analysis Panel - Sidebar */}
      <div className="w-96 bg-gray-50 p-4 shadow-lg overflow-y-auto">
        <AnalysisPanel />
      </div>
    </div>
  );
}

export default App;
