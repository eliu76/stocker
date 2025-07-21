import React, { useRef, useEffect } from "react";
import Chart from "chart.js/auto";

const StockPerformanceChart = ({ prices, ticker }) => {
  const canvasRef = useRef(null);

  useEffect(() => {
    if (!prices || prices.length === 0) return;

    const ctx = canvasRef.current.getContext("2d");

    if (canvasRef.current.chartInstance) {
      canvasRef.current.chartInstance.destroy();
    }

    const chartInstance = new Chart(ctx, {
      type: "line",
      data: {
        labels: prices.map(p => p.date),
        datasets: [
          {
            label: `${ticker} Price`,
            data: prices.map(p => p.close),
            fill: false,
            borderColor: "blue",
            tension: 0.1
          }
        ]
      },
      options: {
        responsive: true,
        plugins: {
          legend: { display: true }
        },
        scales: {
          x: { title: { display: true, text: "Date" } },
          y: { title: { display: true, text: "Price ($)" } }
        }
      }
    });

    canvasRef.current.chartInstance = chartInstance;

  }, [prices, ticker]);

  return (
    <div style={{ width: "100%", height: "400px" }}>
      <canvas ref={canvasRef}></canvas>
    </div>
  );
};

export default StockPerformanceChart;
