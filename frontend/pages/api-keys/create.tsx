import axios from "axios";
import {
  Button,
  Form,
  Input,
  Switch,
  DatePicker,
  Typography,
  notification,
} from "antd";
import { useState } from "react";
import { DateTime } from "luxon";

const { Title } = Typography;

export default function Home() {
  const [loading, setLoading] = useState(false);

  const onFinish = async (values: any) => {
    setLoading(true);

    const data = {
      name: values.name,
      valid_until: values.valid_until
        ? DateTime.fromJSDate(values.valid_until).toSeconds()
        : -1,
      credits: values.credits || -1,
      enabled: values.enabled || true,
    };

    try {
      const response = await axios.post("/admin/api-keys/", data, {
        headers: {
          "Content-Type": "application/json",
        },
      });

      notification.success({
        message: "API Key Created Successfully",
      });
    } catch (error) {
      notification.error({
        message: "Error",
        description: "There was an error creating the API Key.",
      });
    }

    setLoading(false);
  };

  return (
    <>
      <section style={{ textAlign: "center", marginTop: 48, marginBottom: 40 }}>
        <Title level={2} style={{ marginBottom: 0 }}>
          Create API Key
        </Title>
        <Form
          name="create-api-key"
          layout="vertical"
          style={{ maxWidth: 600, margin: "auto" }}
          onFinish={onFinish}
          autoComplete="off"
        >
          <Form.Item
            label="Name"
            name="name"
            rules={[
              {
                required: true,
                message: "Please input a name for the API key!",
              },
            ]}
          >
            <Input />
          </Form.Item>

          <Form.Item label="Valid Until" name="valid_until">
            <DatePicker showTime />
          </Form.Item>

          <Form.Item label="Credits" name="credits">
            <Input type="number" />
          </Form.Item>

          <Form.Item label="Enabled" name="enabled" valuePropName="checked">
            <Switch />
          </Form.Item>

          <Form.Item>
            <Button type="primary" htmlType="submit" loading={loading}>
              Create API Key
            </Button>
          </Form.Item>
        </Form>
      </section>
    </>
  );
}
