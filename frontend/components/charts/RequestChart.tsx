import {
  LineChart,
  Line,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { AggregatedDataPoint, formatXAxis } from "../../utils/charts";

export default function RequestChart({
  data,
}: {
  data: AggregatedDataPoint[];
}) {
  return (
    <ResponsiveContainer width="100%" height={500}>
      <LineChart data={data} margin={{ right: 50, left: 30, top: 5 }}>
        <CartesianGrid
          strokeDasharray="4 3"
          strokeWidth={1}
          strokeOpacity={0.8}
          horizontal={true}
          vertical={false}
        />
        <Line type="monotone" dataKey="amount" stroke="#000" />
        <XAxis
          dataKey="timestamp"
          axisLine={false}
          padding={{ left: 0 }}
          minTickGap={10}
          tickFormatter={formatXAxis}
          angle={-45}
          textAnchor="end"
          height={105}
        />
        <YAxis dataKey="amount" padding={{ top: 0 }} allowDecimals={false} />
        <Tooltip
          labelFormatter={(value) => formatXAxis(value)}
          formatter={(value) => [value as number, "Requests"]}
          cursor={{ fill: "#808080", fillOpacity: 0.3 }}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}
