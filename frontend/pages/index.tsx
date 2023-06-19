import { Select, Typography } from "antd";

const { Title } = Typography;

export default function Home() {
  return (
    <>
      <section style={{ textAlign: "center", marginTop: 48, marginBottom: 40 }}>
        <Title level={2} style={{ marginBottom: 0 }}>
          Validator Endpoint
        </Title>
      </section>
    </>
  );
}
