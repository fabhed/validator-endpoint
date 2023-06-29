import { Card, Col, Row, Statistic } from "antd";
import { DateTime } from "luxon";
import { useCount } from "../SWR/useCount";

export default function Stats() {
  const { count: count24h, isLoading: count24hIsLoading } = useCount({
    start: DateTime.now().minus({ days: 1 }).toUnixInteger()!,
  });
  const { count: count24hKeys, isLoading: count24hKeysIsLoading } = useCount({
    start: DateTime.now().minus({ days: 1 }).toUnixInteger()!,
    unique_api_keys: true,
  });

  return (
    <Row gutter={16}>
      <Col span={12}>
        <Card bordered={false}>
          <Statistic
            title="Requests 24h"
            value={count24h}
            precision={0}
            loading={count24hIsLoading}
          />
        </Card>
      </Col>
      <Col span={12}>
        <Card bordered={false}>
          <Statistic
            value={count24hKeys}
            title="Unique keys 24h"
            precision={0}
            loading={count24hKeysIsLoading}
          />
        </Card>
      </Col>
    </Row>
  );
}
