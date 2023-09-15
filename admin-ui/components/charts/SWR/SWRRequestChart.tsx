import { QuestionCircleOutlined } from "@ant-design/icons";
import { Space, Tooltip, Typography } from "antd";
import { DateTime, Duration } from "luxon";
import { useState } from "react";
import useSWR from "swr";
import { aggregateGroupData } from "../../../utils/charts";
import fetcher from "../../../utils/fetcher";
import RequestChart, { RequestChartDataPoint } from "../RequestChart";
import { DurationSelectors } from "../helpers/DurationSelector";
import React from "react";
import { RequestLogEntry } from "../../../utils/api-types";
const { Title } = Typography;

export default function SWRRequestChart() {
  const [bucketDuration, setBucketDuration] = useState(
    Duration.fromObject({ hours: 1 })
  );
  const [historyDuration, setHistoryDuration] = useState(
    Duration.fromObject({ weeks: 1 })
  );

  const start = DateTime.now().minus(historyDuration).toSeconds().toFixed(0);

  const { data: successData, error: successError } = useSWR<RequestLogEntry[]>(
    `/admin/logs?is_success=true&start=${start}`,
    fetcher
  );
  const { data: failureData, error: failureError } = useSWR<RequestLogEntry[]>(
    `/admin/logs?is_success=false&start=${start}`,
    fetcher
  );

  if (successError || failureError) return <div>Failed to load data</div>;
  if (!successData || !failureData) return <div>Loading...</div>;

  const data = aggregateGroupData<RequestLogEntry, RequestChartDataPoint>({
    data: [
      ...successData.map((s) => ({ ...s, status: "success" })),
      ...failureData.map((s) => ({ ...s, status: "error" })),
    ],
    bucketSize: bucketDuration.as("seconds"),
    groupBy: "status",
    groups: ["success", "error"],
  });
  return (
    <>
      <div style={{ marginLeft: 80 }}>
        <Space size="large" wrap>
          <Title level={2} style={{ whiteSpace: "nowrap" }}>
            API Usage
            <Tooltip title="The graph shows the amount of successful and failed requests sent to the api.">
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
      <RequestChart data={data}></RequestChart>
    </>
  );
}
