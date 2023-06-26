import React, { useState, useEffect } from "react";
import {
  Typography,
  Space,
  Form,
  Input,
  Button,
  message,
  Switch,
  InputNumber,
} from "antd";
import useSWR, { mutate } from "swr";
import axios from "axios";
import fetcher from "../utils/fetcher";
import { getErrorMessageFromResponse } from "../utils/api-handlers";
import { EditableField } from "../components/EditableField";

const { Title } = Typography;

const apiUrl = "/admin/config";

interface GlobalRateLimit {
  times: number;
  seconds: number;
}

interface Configuration {
  hotkey_mnemonic?: string;
  hotkey_pubkey?: string;
  validator_auth_strategy?: string;
  global_rate_limits?: GlobalRateLimit[];
  rate_limiting_enabled?: boolean;
  redis_url?: string;
}

export default function Configuration() {
  const { data: configData, error: configError } = useSWR<Configuration>(
    apiUrl,
    fetcher
  );

  const [configValues, setConfigValues] = useState<Configuration>({});
  const [editing, setEditing] = useState(false);

  useEffect(() => {
    setConfigValues(configData || {});
  }, [configData]);

  const handleUpdateConfigValue = async (key, value) => {
    try {
      await axios.post(apiUrl, { key, value });
      message.success(`Configuration for ${key} updated successfully.`);
      mutate(apiUrl); // Re-fetch the data
    } catch (error: any) {
      message.error(
        `Couldn't save ${key}: ${getErrorMessageFromResponse(error)}`
      );
      throw error;
    }
  };

  const handleAddRateLimit = () => {
    setConfigValues({
      ...configValues,
      global_rate_limits: [
        ...(configValues.global_rate_limits || []),
        { times: 0, seconds: 0 },
      ],
    });
  };

  const handleRemoveRateLimit = (index) => {
    const newRateLimits = [...(configValues.global_rate_limits || [])];
    newRateLimits.splice(index, 1);
    setConfigValues({ ...configValues, global_rate_limits: newRateLimits });
  };

  return (
    <>
      <section style={{ marginBottom: 40 }}>
        <Space size={"large"} direction="vertical" style={{ display: "flex" }}>
          <div>
            <Title style={{ marginBottom: 5 }}>Configuration</Title>
            <p style={{ margin: 0 }}>
              The api server will have to be restarted for changes to take
              effect.
            </p>
          </div>
          {configError && <div>Error loading configuration</div>}
          <Form layout="vertical">
            <Form.Item label="Hotkey Mnemonic">
              <EditableField
                initialValue={configValues.hotkey_mnemonic}
                name="hotkey_mnemonic"
                onUpdate={(v) => handleUpdateConfigValue("hotkey_mnemonic", v)}
                displayValueAsInput
                onChange={() => {}}
                onCancel={() => {}}
              />
            </Form.Item>
            <Form.Item label="Hotkey Public Key">
              <EditableField
                initialValue={configValues.hotkey_pubkey}
                name="hotkey_pubkey"
                onUpdate={(v) => handleUpdateConfigValue("hotkey_pubkey", v)}
                displayValueAsInput
                onChange={() => {}}
                onCancel={() => {}}
              />
            </Form.Item>
            {/* <Form.Item label="Validator Auth Strategy">
              <EditableField
                initialValue={configValues.validator_auth_strategy}
                name="validator_auth_strategy"
                onUpdate={(v) =>
                  handleUpdateConfigValue("validator_auth_strategy", v)
                }
                displayValueAsInput
                onChange={() => {}}
                onCancel={() => {}}
              />
            </Form.Item> */}
            <Form.Item label="Redis URL">
              <EditableField
                initialValue={configValues.redis_url}
                name="redis_url"
                onUpdate={(v) => handleUpdateConfigValue("redis_url", v)}
                displayValueAsInput
                onChange={() => {}}
                onCancel={() => {}}
              />
            </Form.Item>
            <Title level={3}>
              <Space>
                Global Rate Limits
                <Switch
                  checked={configValues.rate_limiting_enabled}
                  title="Rate Limiting Enabled"
                  onChange={(checked) => {
                    setConfigValues({
                      ...configValues,
                      rate_limiting_enabled: checked,
                    });
                    handleUpdateConfigValue("rate_limiting_enabled", checked);
                  }}
                />
                <Button
                  type="dashed"
                  disabled={!editing}
                  onClick={handleAddRateLimit}
                >
                  Add Rate Limit
                </Button>
              </Space>
            </Title>
            <Space direction="vertical">
              {(configValues.global_rate_limits || []).map(
                (rateLimit, index) => (
                  <Space key={index}>
                    <Form.Item label="Times">
                      <InputNumber
                        min={0}
                        value={rateLimit.times}
                        disabled={!editing}
                        onChange={(value) => {
                          const newRateLimits = [
                            ...configValues.global_rate_limits!,
                          ];
                          newRateLimits[index].times = value || 0;
                          setConfigValues({
                            ...configValues,
                            global_rate_limits: newRateLimits,
                          });
                        }}
                      />
                    </Form.Item>
                    <Form.Item label="Seconds">
                      <InputNumber
                        min={0}
                        value={rateLimit.seconds}
                        disabled={!editing}
                        onChange={(value) => {
                          const newRateLimits = [
                            ...configValues.global_rate_limits!,
                          ];
                          newRateLimits[index].seconds = value || 0;
                          setConfigValues({
                            ...configValues,
                            global_rate_limits: newRateLimits,
                          });
                        }}
                      />
                    </Form.Item>
                    {editing && (
                      <Button onClick={() => handleRemoveRateLimit(index)}>
                        Remove
                      </Button>
                    )}
                  </Space>
                )
              )}
            </Space>
            {editing ? (
              <Form.Item>
                <Button
                  type="primary"
                  onClick={async () => {
                    // Save the rate limits
                    await handleUpdateConfigValue(
                      "global_rate_limits",
                      configValues.global_rate_limits
                    );
                    setEditing(false);
                  }}
                >
                  Save Rate Limits
                </Button>
              </Form.Item>
            ) : (
              <Form.Item>
                <Button
                  type={editing ? "primary" : "default"}
                  onClick={() => {
                    if (editing) {
                    }
                    setEditing(!editing);
                  }}
                >
                  {editing ? "Save" : "Edit Rate Limits"}
                </Button>
              </Form.Item>
            )}
          </Form>
        </Space>
      </section>
    </>
  );
}
