import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { formatXAxis } from "../../utils/charts";
import { green, red } from "@ant-design/colors";

export interface RequestChartDataPoint {
  success: number;
  error: number;
  timestamp: number;
}

export default function RequestChart({
  data,
}: {
  data: RequestChartDataPoint[];
}) {
  return (
    <ResponsiveContainer width="100%" height={500}>
      <AreaChart data={data} margin={{ right: 50, left: 30, top: 5 }}>
        <CartesianGrid
          strokeDasharray="4 3"
          strokeWidth={1}
          strokeOpacity={0.8}
          horizontal={true}
          vertical={false}
        />
        <Area
          type="monotone"
          dataKey="error"
          stroke={red[6]}
          fill={red[4]}
          fillOpacity={0.8}
          stackId="1"
          order={1}
        />
        <Area
          type="monotone"
          dataKey="success"
          stroke={green[8]}
          fill={green[6]}
          fillOpacity={0.8}
          stackId="1"
          order={0}
        />
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
        <YAxis padding={{ top: 0 }} allowDecimals={false} />
        <Tooltip
          labelFormatter={(value) => formatXAxis(value)}
          formatter={(value, key) => {
            return [
              value as number,
              key === "error" ? "Failed requests" : "Successful Requests",
            ];
          }}
          itemSorter={(item) => {
            switch (item.dataKey) {
              case "success":
                return 1;
              case "error":
                return 2;
              default:
                return 3;
            }
          }}
          cursor={{ fill: "#808080", fillOpacity: 0.3 }}
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}
