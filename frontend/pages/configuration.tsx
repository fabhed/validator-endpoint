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
  Tooltip,
} from "antd";
import useSWR, { mutate } from "swr";
import axios from "axios";
import fetcher from "../utils/fetcher";
import { getErrorMessageFromResponse } from "../utils/api-handlers";
import { EditableField } from "../components/EditableField";
import { QuestionCircleOutlined } from "@ant-design/icons";
import { RateLimitForm } from "../components/RateLimitForm";

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
  openai_filter_enabled?: boolean;
  openai_api_key?: string;
}

export default function Configuration() {
  const { data: configData, error: configError } = useSWR<Configuration>(
    apiUrl,
    fetcher
  );

  const [configValues, setConfigValues] = useState<Configuration>({});

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

  const onRateLimitsChange = (rateLimits) => {
    setConfigValues({
      ...configValues,
      global_rate_limits: rateLimits,
    });
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
            {/* <Form.Item label="Hotkey Public Key">
              <EditableField
                initialValue={configValues.hotkey_pubkey}
                name="hotkey_pubkey"
                onUpdate={(v) => handleUpdateConfigValue("hotkey_pubkey", v)}
                displayValueAsInput
                onChange={() => {}}
                onCancel={() => {}}
              />
            </Form.Item> */}
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
            <Form.Item
              label="Redis URL"
              help="Redis is only needed if rate limits are used."
            >
              <EditableField
                initialValue={configValues.redis_url}
                name="redis_url"
                onUpdate={(v) => handleUpdateConfigValue("redis_url", v)}
                displayValueAsInput
                onChange={() => {}}
                onCancel={() => {}}
              />
            </Form.Item>
            <Title level={3} style={{ marginTop: "3rem" }}>
              <Space>
                OpenAI Filtering
                <Tooltip title="Filters incoming prompts via OpenAI's Moderation endpoint. This is a free Service from OpenAI but requires an API-key. Enabling this will add latency to requests, as the moderation check is done before the bittensor network is queried.">
                  <QuestionCircleOutlined
                    style={{
                      marginLeft: "8px",
                      cursor: "help",
                      fontSize: "60%",
                      verticalAlign: "middle",
                    }}
                  />
                </Tooltip>
                <Switch
                  checked={configValues.openai_filter_enabled}
                  title="OpenAI Filtering Enabled"
                  onChange={(checked) => {
                    setConfigValues({
                      ...configValues,
                      openai_filter_enabled: checked,
                    });
                    handleUpdateConfigValue("openai_filter_enabled", checked);
                  }}
                />
              </Space>
            </Title>
            {configValues.openai_filter_enabled && (
              <Form.Item label="OpenAI API Key">
                <EditableField
                  initialValue={configValues.openai_api_key}
                  name="openai_api_key"
                  onUpdate={(v) => handleUpdateConfigValue("openai_api_key", v)}
                  displayValueAsInput
                  onChange={() => {}}
                  onCancel={() => {}}
                />
              </Form.Item>
            )}
            <RateLimitForm
              title="Global Rate Limits"
              enabled={!!configValues.rate_limiting_enabled}
              onEnabledChange={(checked) => {
                setConfigValues({
                  ...configValues,
                  rate_limiting_enabled: checked,
                });
                handleUpdateConfigValue("rate_limiting_enabled", checked);
              }}
              rateLimits={configValues.global_rate_limits || []}
              onRateLimitsChange={onRateLimitsChange}
              onSave={async () => {
                // Save the rate limits
                await handleUpdateConfigValue(
                  "global_rate_limits",
                  configValues.global_rate_limits
                );
              }}
            ></RateLimitForm>
          </Form>
        </Space>
      </section>
    </>
  );
}
