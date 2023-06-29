import { Space, Form, InputNumber, Button, Typography, Switch } from "antd";
import React from "react";
import { useState } from "react";

const { Title } = Typography;

export interface RateLimit {
  times: number;
  seconds: number;
}

export function RateLimitForm({
  enabled,
  onEnabledChange,
  rateLimits,
  onRateLimitsChange,
  onSave,
  title,
}: {
  enabled: boolean;
  onEnabledChange: (enabled: boolean) => void;
  rateLimits: RateLimit[];
  onRateLimitsChange: (rateLimits: RateLimit[]) => void;
  onSave: (rateLimits: RateLimit[]) => Promise<void>;
  title: string;
}) {
  const [isEditing, setIsEditing] = useState(false);

  const handleAddRateLimit = () => {
    let newRateLimits = [...(rateLimits || []), { times: 0, seconds: 0 }];
    onRateLimitsChange(newRateLimits);
  };

  const handleRemoveRateLimit = (index) => {
    const newRateLimits = [...(rateLimits || [])];
    newRateLimits.splice(index, 1);
    onRateLimitsChange(newRateLimits);
  };

  return (
    <div>
      <Title level={3}>
        <Space>
          {title}
          <Switch
            checked={enabled}
            title="Rate Limiting Enabled"
            onChange={onEnabledChange}
          />
          <Button
            type="dashed"
            disabled={!isEditing}
            onClick={handleAddRateLimit}
          >
            Add Rate Limit
          </Button>
        </Space>
      </Title>
      <Space direction="vertical">
        {(rateLimits || []).map((rateLimit, index) => (
          <Space key={index}>
            <Form.Item label="Times">
              <InputNumber
                min={0}
                value={rateLimit.times}
                disabled={!isEditing}
                onChange={(value) => {
                  const newRateLimits = [...rateLimits];
                  newRateLimits[index].times = value || 0;
                  onRateLimitsChange(newRateLimits);
                }}
              />
            </Form.Item>
            <Form.Item label="Seconds">
              <InputNumber
                min={0}
                value={rateLimit.seconds}
                disabled={!isEditing}
                onChange={(value) => {
                  const newRateLimits = [...rateLimits];
                  newRateLimits[index].seconds = value || 0;
                  onRateLimitsChange(newRateLimits);
                }}
              />
            </Form.Item>
            {isEditing && (
              <Button onClick={() => handleRemoveRateLimit(index)}>
                Remove
              </Button>
            )}
          </Space>
        ))}
      </Space>
      {isEditing ? (
        <Form.Item>
          <Button
            type="primary"
            onClick={async () => {
              await onSave(rateLimits);
              setIsEditing(false);
            }}
          >
            Save Rate Limits
          </Button>
        </Form.Item>
      ) : (
        <Form.Item>
          <Button
            type={isEditing ? "primary" : "default"}
            onClick={() => {
              if (isEditing) {
              }
              setIsEditing(!isEditing);
            }}
          >
            {isEditing ? "Save" : "Edit Rate Limits"}
          </Button>
        </Form.Item>
      )}
    </div>
  );
}
