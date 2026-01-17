import React, { useState } from 'react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, Filler);

export default function YieldChart() {
  const [range, setRange] = useState('month');

  const data = {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
    datasets: [
      {
        label: 'Predicted Yield (tons/ha)',
        data: [4.2, 4.5, 4.3, 4.8, 5.1, 4.9],
        borderColor: '#00ff88',
        backgroundColor: 'rgba(0, 255, 136, 0.1)',
        borderWidth: 3,
        tension: 0.4,
        fill: true
      },
      {
        label: 'Actual Yield (tons/ha)',
        data: [4.0, 4.4, 4.2, 4.7, 5.0, 4.8],
        borderColor: '#0088ff',
        backgroundColor: 'rgba(0, 136, 255, 0.1)',
        borderWidth: 3,
        tension: 0.4,
        fill: true
      }
    ]
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { labels: { color: '#fff', font: { size: 14 } } }
    },
    scales: {
      y: { 
        beginAtZero: true, 
        grid: { color: 'rgba(0, 255, 136, 0.1)' },
        ticks: { color: '#fff' }
      },
      x: { 
        grid: { color: 'rgba(0, 255, 136, 0.1)' },
        ticks: { color: '#fff' }
      }
    }
  };

  return (
    <div className="chart-container">
      <div className="chart-header">
        <h3 className="section-title">📈 Yield Trends Analysis</h3>
        <div className="chart-controls">
          <button className={`chart-btn ${range === 'week' ? 'active' : ''}`} onClick={() => setRange('week')}>Week</button>
          <button className={`chart-btn ${range === 'month' ? 'active' : ''}`} onClick={() => setRange('month')}>Month</button>
          <button className={`chart-btn ${range === 'year' ? 'active' : ''}`} onClick={() => setRange('year')}>Year</button>
        </div>
      </div>
      <div style={{ height: '350px' }}>
        <Line data={data} options={options} />
      </div>
    </div>
  );
}