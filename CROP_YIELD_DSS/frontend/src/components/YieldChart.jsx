import React from 'react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS, CategoryScale, LinearScale, PointElement,
  LineElement, Title, Tooltip, Legend, Filler
} from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, Filler);

export default function YieldChart({ chartData }) {
  if (!chartData || !chartData.labels.length) {
    return (
      <div className="chart-container" style={{ textAlign: 'center', padding: '50px' }}>
        <p style={{ opacity: 0.5 }}>Insufficient data for Yield Gap analysis.</p>
      </div>
    );
  }

  const data = {
    labels: chartData.labels,
    datasets: [
      {
        label: chartData.datasets[0].label,
        data: chartData.datasets[0].data,
        borderColor: '#0088ff',
        backgroundColor: 'rgba(0, 136, 255, 0.1)',
        borderWidth: 2,
        borderDash: [5, 5], // Dashed for "Baseline/Potential"
        tension: 0.4,
        fill: true
      },
      {
        label: chartData.datasets[1].label,
        data: chartData.datasets[1].data,
        borderColor: '#00ff88',
        backgroundColor: 'rgba(0, 255, 136, 0.1)',
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
      legend: { labels: { color: '#fff', font: { size: 12, weight: '600' } } },
      tooltip: { backgroundColor: 'rgba(10, 14, 39, 0.9)', titleColor: '#00ff88', bodyColor: '#fff', borderColor: '#00ff88', borderWidth: 1 }
    },
    scales: {
      y: { 
        beginAtZero: true, 
        grid: { color: 'rgba(255, 255, 255, 0.05)' },
        ticks: { color: 'rgba(255, 255, 255, 0.7)', callback: (v) => `${v} t/ha` }
      },
      x: { 
        grid: { display: false },
        ticks: { color: 'rgba(255, 255, 255, 0.7)' }
      }
    }
  };

  return (
    <div className="chart-container">
      <div className="chart-header">
        <h3 className="section-title">📈 Yield Gap Analysis (Baseline vs. Prediction)</h3>
      </div>
      <div style={{ height: '350px' }}>
        <Line data={data} options={options} />
      </div>
      <p style={{ fontSize: '11px', opacity: 0.5, marginTop: '15px' }}>
        * Baseline derived from SPAM 2020 v2.0 Global Datasets. Predictions processed via Hybrid ensemble logic.
      </p>
    </div>
  );
}