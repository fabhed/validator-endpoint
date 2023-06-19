import useSWR from "swr";
import fetcher from "../../../utils/fetcher";
import RequestChart from "../RequestChart";
import { aggregateData } from "../../../utils/charts";
import { DurationSelectors } from "../helpers/DurationSelector";
import { Duration } from "luxon";
import { useState } from "react";
import { Space, Tooltip, Typography } from "antd";
import { QuestionCircleOutlined } from "@ant-design/icons";
const { Title } = Typography;

export default function SWRRequestChart() {
  const [bucketDuration, setBucketDuration] = useState(
    Duration.fromObject({ hours: 1 })
  );
  const [historyDuration, setHistoryDuration] = useState(
    Duration.fromObject({ weeks: 1 })
  );

  const { data, error } = useSWR<RequestLogEntry[]>("/admin/logs", fetcher);

  if (error) return <div>Failed to load data</div>;
  if (!data) return <div>Loading...</div>;

  // Transform the data into a suitable format for the chart
  const chartData = aggregateData<RequestLogEntry>({
    data,
    bucketSize: bucketDuration.as("seconds"),
  });
  return (
    <>
      <div style={{ marginLeft: 80 }}>
        <Space size="large" wrap>
          <Title level={2} style={{ whiteSpace: "nowrap" }}>
            API Usage
            <Tooltip title="The graph shows the amount of valid requests sent to the api.">
              <QuestionCircleOutlined
                style={{
                  marginLeft: "8px",
                  cursor: "help",
                  fontSize: "60%",
                  verticalAlign: "middle",
                }}
              />
            </Tooltip>
          </Title>
          <DurationSelectors
            bucketDuration={bucketDuration}
            setBucketDuration={setBucketDuration}
            historyDuration={historyDuration}
            setHistoryDuration={setHistoryDuration}
          />
        </Space>
      </div>
      <RequestChart data={chartData}></RequestChart>
    </>
  );
}
