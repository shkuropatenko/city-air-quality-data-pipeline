import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

function AirQualityChart({ observations }) {
  if (!observations?.length) {
    return null;
  }

  const chartData = observations.map((observation) => ({
    time: new Date(observation.observed_at).toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit",
    }),
    pm2_5: observation.pm2_5,
    pm10: observation.pm10,
    o3: observation.o3,
  }));

  return (
    <section className="dashboard-panel chart-panel">
      <div className="chart-header">
        <div>
          <p className="section-eyebrow">Historical measurements</p>
          <h2>Air Quality Over Time</h2>
        </div>

        <span className="chart-unit">µg/m³</span>
      </div>

      <div className="chart-container">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart
            data={chartData}
            margin={{ top: 10, right: 20, left: 0, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" vertical={false} />

            <XAxis
              dataKey="time"
              tickLine={false}
              axisLine={false}
              minTickGap={40}
            />

            <YAxis tickLine={false} axisLine={false} />

            <Tooltip />
            <Legend />

            <Line
              type="monotone"
              dataKey="pm2_5"
              name="PM2.5"
              stroke="#2563eb"
              strokeWidth={2}
              dot={false}
            />

            <Line
              type="monotone"
              dataKey="pm10"
              name="PM10"
              stroke="#7c3aed"
              strokeWidth={2}
              dot={false}
            />

            <Line
              type="monotone"
              dataKey="o3"
              name="Ozone"
              stroke="#0891b2"
              strokeWidth={2}
              dot={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </section>
  );
}

export default AirQualityChart;
