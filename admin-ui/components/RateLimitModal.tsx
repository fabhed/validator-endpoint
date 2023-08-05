import { Form, Input, Modal, Typography, message } from "antd";
import { useEffect, useState } from "react";
import { RateLimit, RateLimitForm } from "./RateLimitForm";
import { ApiKeyDataType } from "../pages/api-keys";
import axios from "axios";
import { mutate } from "swr";
import { RateLimitEntry } from "../utils/api-types";
import React from "react";

const { Paragraph, Title } = Typography;

export const RateLimitModal = ({
  apiKey,
  open,
  setOpen,
}: {
  apiKey: ApiKeyDataType | null;
  open: boolean;
  setOpen: (open: boolean) => void;
}) => {
  const [enabled, setEnabled] = useState(false);
  const [rateLimits, setRateLimits] = useState<RateLimit[]>([]);
  useEffect(() => {
    if (!apiKey) return;
    setEnabled(apiKey.rate_limits_enabled || false);
    setRateLimits(apiKey.rate_limits ? JSON.parse(apiKey.rate_limits) : []);
  }, [apiKey]);

  if (!apiKey) return null;

  const save = async (values: {
    rate_limits_enabled?: boolean;
    rate_limits?: RateLimitEntry[];
  }) => {
    try {
      await axios.patch(`/admin/api-keys/${apiKey.id}/`, values);
      message.success("Successfully saved changes");
      mutate("/admin/api-keys/");
    } catch (err) {
      message.error("Failed to save changes");
      console.error(err);
    }
  };

  return (
    <>
      <Modal
        open={open}
        onCancel={() => setOpen(false)}
        footer={null}
        width="90vw"
      >
        <RateLimitForm
          title="Specific Rate Limits"
          enabled={enabled}
          onEnabledChange={(enabled) => {
            setEnabled(enabled);
            save({ rate_limits_enabled: enabled });
            // update in api
          }}
          rateLimits={rateLimits}
          onRateLimitsChange={setRateLimits}
          onSave={(rateLimits) => save({ rate_limits: rateLimits })}
        ></RateLimitForm>
        You are viewing the rate limits for the API key:
        <Paragraph>
          <pre>{apiKey?.api_key}</pre>
        </Paragraph>
      </Modal>
    </>
  );
};
