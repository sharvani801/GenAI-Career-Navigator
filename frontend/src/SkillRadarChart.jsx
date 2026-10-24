
import {
  ResponsiveContainer,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  Legend,
  Tooltip,
} from "recharts";

export default function SkillRadarChart({ data = [] }) {
  const chartData = Array.isArray(data)
    ? data.filter(
        (item) =>
          item &&
          typeof item.skill === "string" &&
          Number.isFinite(Number(item.current)) &&
          Number.isFinite(Number(item.required))
      )
    : [];

  if (chartData.length === 0) {
    return (
      <div className="flex min-h-64 items-center justify-center text-gray-500">
        Analyze a career to see your skill radar chart.
      </div>
    );
  }

  return (
    <div className="w-full">
      <ResponsiveContainer width="100%" height={350}>
        <RadarChart
          data={chartData}
          outerRadius="72%"
          margin={{ top: 20, right: 35, bottom: 20, left: 35 }}
        >
          <PolarGrid />

          <PolarAngleAxis
            dataKey="skill"
            tick={{ fontSize: 11 }}
          />

          <PolarRadiusAxis
            angle={90}
            domain={[0, 100]}
            tickCount={6}
          />

          <Tooltip />
          <Legend />

          <Radar
            name="Current Skills"
            dataKey="current"
            stroke="#2563eb"
            fill="#2563eb"
            fillOpacity={0.35}
          />

          <Radar
            name="Required Skills"
            dataKey="required"
            stroke="#16a34a"
            fill="#16a34a"
            fillOpacity={0.15}
          />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  );
}
