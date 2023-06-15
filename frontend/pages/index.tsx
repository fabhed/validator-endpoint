import {
  Form,
  Select,
  InputNumber,
  DatePicker,
  Switch,
  Slider,
  Button,
  Rate,
  Typography,
  Space,
  Divider,
} from "antd";
import Link from "next/link";

const { Option } = Select;
const { Title } = Typography;

export default function Home() {
  return (
    <>
      <section style={{ textAlign: "center", marginTop: 48, marginBottom: 40 }}>
        <Title level={2} style={{ marginBottom: 0 }}>
          Validator Endpoint
        </Title>
        <Link href="/api-keys/create">Create API key</Link>
      </section>
    </>
  );
}
