
import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Legend,
  ResponsiveContainer,
  Tooltip,
} from "recharts";

const sampleData = [
  { skill: "Python", current: 75, required: 90 },
  { skill: "SQL", current: 60, required: 85 },
  { skill: "Machine Learning", current: 50, required: 90 },
  { skill: "Data Analysis", current: 80, required: 85 },
  { skill: "Communication", current: 70, required: 80 },
];

export default function SkillRadarChart({ data = sampleData }) {
  return (
    <div
      style={{
        width: "100%",
        height: 400,
        padding: "20px",
        boxSizing: "border-box",
      }}
    >
      <h3 style={{ marginBottom: "15px" }}>
        Current Skills vs Required Skills
      </h3>

      <ResponsiveContainer width="100%" height="85%">
        <RadarChart data={data} outerRadius="65%">
          <PolarGrid />

          <PolarAngleAxis dataKey="skill" />

          <PolarRadiusAxis
            angle={30}
            domain={[0, 100]}
            tickCount={6}
          />

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
            stroke="#9333ea"
            fill="#9333ea"
            fillOpacity={0.2}
          />

          <Tooltip />
          <Legend />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  );
}
