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
  console.log(configValues);
  const [editing, setEditing] = useState(false);

  useEffect(() => {
    console.log(configData);
    setConfigValues(configData || {});
  }, [configData]);

  const handleUpdateConfigValue = async (key, value) => {
    try {
      await axios.post(apiUrl, { key, value });

      message.success(`Configuration for ${key} updated successfully.`);
      mutate(apiUrl); // Re-fetch the data
    } catch (error: any) {
      debugger;

      message.error(
        `Couldn't save ${key}: ${getErrorMessageFromResponse(error)}`
      );
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
        {/* <pre>{JSON.stringify(configValues, null, 2)}</pre> */}
        <Space size={"large"} direction="vertical" style={{ display: "flex" }}>
          <Title>
            <div style={{ display: "flex", alignItems: "center", gap: 15 }}>
              Configuration
              <Button
                onClick={() => setEditing(!editing)}
                style={{ display: "inline-block" }}
              >
                {editing ? "Cancel Editing" : "Edit Config"}
              </Button>
            </div>
          </Title>
          {configError && <div>Error loading configuration</div>}
          <Form layout="vertical">
            <Form.Item label="Hotkey Mnemonic">
              <Input
                value={configValues.hotkey_mnemonic}
                disabled={!editing}
                onChange={(e) =>
                  setConfigValues({
                    ...configValues,
                    hotkey_mnemonic: e.target.value,
                  })
                }
              />
            </Form.Item>

            <Form.Item label="Hotkey Public Key">
              <Input
                value={configValues.hotkey_pubkey}
                disabled={!editing}
                onChange={(e) =>
                  setConfigValues({
                    ...configValues,
                    hotkey_pubkey: e.target.value,
                  })
                }
              />
            </Form.Item>

            <Form.Item label="Validator Auth Strategy">
              <Input
                value={configValues.validator_auth_strategy}
                disabled={!editing}
                onChange={(e) =>
                  setConfigValues({
                    ...configValues,
                    validator_auth_strategy: e.target.value,
                  })
                }
              />
            </Form.Item>
            <Form.Item label="Redis URL">
              <Input
                value={configValues.redis_url}
                disabled={!editing}
                onChange={(e) =>
                  setConfigValues({
                    ...configValues,
                    redis_url: e.target.value,
                  })
                }
              />
            </Form.Item>

            <Title level={3}>
              <Space>
                Global Rate Limits
                <Switch
                  checked={configValues.rate_limiting_enabled}
                  title="Rate Limiting Enabled"
                  disabled={!editing}
                  onChange={(checked) =>
                    setConfigValues({
                      ...configValues,
                      rate_limiting_enabled: checked,
                    })
                  }
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

            {editing && (
              <Form.Item>
                <Button
                  type="primary"
                  onClick={() =>
                    Object.keys(configValues).forEach((key) =>
                      handleUpdateConfigValue(key, configValues[key])
                    )
                  }
                >
                  Update Configuration
                </Button>
              </Form.Item>
            )}
          </Form>
        </Space>
      </section>
    </>
  );
}
