import {
  CopyOutlined,
  EditOutlined,
  QuestionCircleOutlined,
  FieldTimeOutlined,
} from "@ant-design/icons";
import {
  Button,
  DatePicker,
  Form,
  FormInstance,
  Input,
  InputRef,
  Space,
  Switch,
  Table,
  Tooltip,
  message,
} from "antd";
import axios from "axios";
import dayjs from "dayjs";
import "dayjs/plugin/utc";
import { DateTime } from "luxon";
import React, { useContext, useEffect, useRef, useState } from "react";
import useSWR, { mutate } from "swr";
import { APIKeyOperations } from "../../components/APIKeyOperations";
import fetcher from "../../utils/fetcher";
import { green, red } from "@ant-design/colors";
import { RateLimitModal } from "../../components/RateLimitModal";
import { RateLimit } from "../../components/RateLimitForm";

export interface ApiKeyDataType {
  key: React.Key;
  form: FormInstance;
  id: number;
  name: string;
  api_key: string;
  api_key_hint: string;
  valid_until: number;
  credits: number;
  request_count: number;
  enabled: boolean;
  requests: number;
  // rate_limits: null | RateLimit[];
  rate_limits: null | string;
  rate_limits_enabled: boolean;
}

const EditableContext = React.createContext<FormInstance<any> | null>(null);

interface EditableRowProps {
  index: number;
}

const EditableRow: React.FC<EditableRowProps> = ({ index, ...props }) => {
  const [form] = Form.useForm();
  return (
    <Form form={form} component={false}>
      <EditableContext.Provider value={form}>
        <tr {...props} />
      </EditableContext.Provider>
    </Form>
  );
};

interface EditableCellProps {
  title: React.ReactNode;
  editable: boolean;
  children: React.ReactNode;
  dataIndex: keyof ApiKeyDataType;
  record: ApiKeyDataType;
}

const EditableCell: React.FC<EditableCellProps> = ({
  title,
  editable,
  children,
  dataIndex,
  record,
  ...restProps
}) => {
  const [editing, setEditing] = useState(false);
  const [hovering, setHovering] = useState(false);

  const [initialValue, setInitialValue] = useState<any>();
  const inputRef = useRef<InputRef>(null);
  const form = useContext(EditableContext)!;

  useEffect(() => {
    if (editing) {
      inputRef.current!.focus();
    }
  }, [editing]);

  const toggleEdit = () => {
    if (!editing) {
      let val: any = record[dataIndex];
      if (dataIndex === "valid_until") {
        if (val == -1) {
          val = undefined;
        } else {
          val = dayjs.unix(val);
        }
      }

      form.setFieldsValue({ [dataIndex]: val });
      setInitialValue(val);
    }
    setEditing(!editing);
  };

  const save = async () => {
    try {
      const values = await form.validateFields();
      toggleEdit();
      if (initialValue === values[dataIndex]) return;
      await axios.patch(`/admin/api-keys/${record.id}/`, values);
      message.success("Successfully saved changes");
      mutate("/admin/api-keys/");
    } catch (err) {
      message.error("Failed to save changes");
      console.error(err);
    }
  };

  const handleMouseEnter = () => {
    setHovering(true);
  };

  const handleMouseLeave = () => {
    setHovering(false);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Escape") {
      form.setFieldsValue({ [dataIndex]: initialValue });
      setEditing(false);
    }
  };

  let childNode = children;

  if (editable) {
    childNode = editing ? (
      <div style={{ display: "flex", gap: 5 }}>
        <Form.Item
          style={{ margin: 0, flexGrow: 1 }}
          name={dataIndex}
          rules={[
            {
              required: true,
              message: `${
                typeof title === "string" ? title : "The field"
              } is required.`,
            },
          ]}
        >
          {dataIndex === "valid_until" ? (
            <DatePicker
              showTime
              style={{ minWidth: 200 }}
              ref={inputRef as any}
              format="YYYY-MM-DD HH:mm"
              onBlur={save}
              onChange={(date) => {
                if (date) {
                  form.setFieldsValue({
                    [dataIndex]: date,
                  });
                } else {
                  form.setFieldsValue({
                    [dataIndex]: -1,
                  });
                }
                save();
              }}
              onKeyDown={handleKeyDown}
              autoFocus
            />
          ) : (
            <Input
              style={{ minWidth: 200 }}
              ref={inputRef}
              onPressEnter={save}
              onBlur={save}
              onKeyDown={handleKeyDown}
            />
          )}
        </Form.Item>
      </div>
    ) : (
      <div
        className="editable-cell-value-wrap"
        style={{ paddingRight: 24, display: "flex", alignItems: "center" }}
      >
        <span style={{ flexGrow: 1 }}>{children}</span>
        {
          <EditOutlined
            style={{
              color: "#1890ff",
              fontSize: "18px",
              cursor: "pointer",
              opacity: hovering ? 1 : 0,
              transition: "opacity 0.3s",
            }}
            onClick={toggleEdit}
          />
        }
      </div>
    );
  }

  return (
    <td
      {...restProps}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
    >
      {childNode}
    </td>
  );
};

export default function ViewApiKeys() {
  const { data, error } = useSWR<ApiKeyDataType[]>("/admin/api-keys/", fetcher);

  const [rateLimitModalOpen, setRateLimitModalOpen] = useState(false);
  const [activeRateLimitApiKey, setActiveRateLimitApiKey] =
    useState<ApiKeyDataType | null>(null);

  const openRateLimitModal = (apiKey: ApiKeyDataType) => {
    setActiveRateLimitApiKey(apiKey);
    setRateLimitModalOpen(true);
  };

  if (error) {
    message.error("An error occurred while fetching the data.");
    return <div>Failed to load</div>;
  }
  if (!data) return <div>Loading...</div>;

  const handleSwitchChange = async (
    record: ApiKeyDataType,
    checked: boolean
  ) => {
    try {
      await axios.patch(`/admin/api-keys/${record.id}/`, { enabled: checked });
      message.success("Status updated successfully");
      mutate("/admin/api-keys/");
    } catch (error) {
      message.error("Failed to update status");
    }
  };

  const handleDelete = async (record: ApiKeyDataType) => {
    try {
      await axios.delete(`/admin/api-keys/${record.id}`);
      message.success("API Key deleted.");
      mutate("/admin/api-keys/");
    } catch (err) {
      message.error("Failed to delete API Key.");
    }
  };

  const columns = [
    {
      title: "ID",
      dataIndex: "id",
      key: "id",
      sorter: (a: ApiKeyDataType, b: ApiKeyDataType) => a.id - b.id,
    },
    {
      title: "Name",
      dataIndex: "name",
      key: "name",
      editable: true,
      sorter: (a: ApiKeyDataType, b: ApiKeyDataType) =>
        a.name.localeCompare(b.name),
    },
    {
      title: "API Key",
      dataIndex: "api_key",
      key: "api_key",
      render: (text: string) => {
        const handleCopy = () => {
          navigator.clipboard
            .writeText(text)
            .then(() => message.success("API Key copied to clipboard"))
            .catch(() => message.error("Failed to copy API Key"));
        };

        return (
          <div style={{ display: "flex", alignItems: "center" }}>
            <span
              style={{
                maxWidth: "100px",
                overflow: "hidden",
                textOverflow: "ellipsis",
                whiteSpace: "nowrap",
              }}
            >
              {text}
            </span>
            <Button
              type="link"
              size="large"
              icon={<CopyOutlined />}
              onClick={handleCopy}
            />
          </div>
        );
      },
    },
    {
      title: "Valid Until",
      dataIndex: "valid_until",
      key: "valid_until",
      render: (text: number) =>
        text === -1
          ? "No Expiration"
          : DateTime.fromSeconds(text).toFormat("yyyy-MM-dd HH:mm"),
      editable: true,
      sorter: (a: ApiKeyDataType, b: ApiKeyDataType) =>
        a.valid_until - b.valid_until,
    },
    {
      title: (
        <span>
          Credits{" "}
          <Tooltip title="A value of -1 represents unlimited credits.">
            <QuestionCircleOutlined />
          </Tooltip>
        </span>
      ),
      dataIndex: "credits",
      key: "credits",
      editable: true,
      filters: [
        { text: "Unlimited", value: -1 },
        { text: "Limited", value: 0 },
      ],
      onFilter: (value: any, record: ApiKeyDataType) => {
        if (value === -1) {
          return record.credits === -1;
        } else {
          return record.credits !== -1;
        }
      },
      sorter: (a: ApiKeyDataType, b: ApiKeyDataType) => a.credits - b.credits,
    },
    {
      title: "Enabled",
      dataIndex: "enabled",
      key: "enabled",
      render: (enabled: boolean, record: ApiKeyDataType) => (
        <Switch
          checked={enabled}
          onChange={(checked: boolean) => handleSwitchChange(record, checked)}
        />
      ),
      filters: [
        { text: "Enabled", value: true },
        { text: "Disabled", value: false },
      ],
      onFilter: (value: any, record: ApiKeyDataType) =>
        record.enabled === value,
    },

    {
      title: "Requests",
      dataIndex: "request_count",
      key: "requests",
      sorter: (a: ApiKeyDataType, b: ApiKeyDataType) =>
        a.request_count - b.request_count,
      render: (requests, record: ApiKeyDataType) => {
        return (
          <Space>
            {requests}
            <Tooltip
              title={`Rate Limits - ${
                record.rate_limits
                  ? "Specific rate limits enabled"
                  : "No specific rate limits"
              }`}
            >
              <Button
                type="link"
                size="small"
                onClick={() => openRateLimitModal(record)}
                style={{ color: record.rate_limits_enabled ? "green" : "" }}
              >
                <FieldTimeOutlined />
              </Button>
            </Tooltip>
          </Space>
        );
      },
    },
    {
      title: "Operation",
      dataIndex: "operation",
      render: (_: unknown, record: ApiKeyDataType, index: number) => {
        return (
          <APIKeyOperations
            prompt="What is 1+1?"
            apiKey={record.api_key}
            url={process.env.NEXT_PUBLIC_API_BASE_URL}
            onDelete={() => handleDelete(record)}
          />
        );
      },
    },
  ];

  const mergedColumns = columns.map((col) => {
    if (!col.editable) {
      return col;
    }
    return {
      ...col,
      onCell: (record: ApiKeyDataType) => ({
        record,
        inputType:
          col.dataIndex === "credits" || col.dataIndex === "valid_until"
            ? "number"
            : "text",
        dataIndex: col.dataIndex,
        title: col.title,
        editable: col.editable,
      }),
    };
  });

  return (
    <div>
      <RateLimitModal
        apiKey={activeRateLimitApiKey}
        open={rateLimitModalOpen}
        setOpen={setRateLimitModalOpen}
      ></RateLimitModal>
      <Button
        type="primary"
        onClick={async () => {
          try {
            await axios.post("/admin/api-keys/", { name: "New API Key" });
            message.success("API Key created.");
            mutate("/admin/api-keys/");
          } catch (err) {
            message.error("Failed to create API Key.");
          }
        }}
        style={{ marginBottom: 16 }}
      >
        Create New API Key
      </Button>
      <Table
        rowClassName={() => "editable-row"}
        components={{
          body: {
            cell: EditableCell,
            row: EditableRow,
          },
        }}
        scroll={{
          x: true,
        }}
        // @ts-ignore
        columns={mergedColumns}
        dataSource={data}
        rowKey="id"
        onRow={(record) => ({
          onMouseEnter: () => {
            if (document) {
              const actionCells = document.querySelectorAll(
                'td > span[style="visibility: hidden;"]'
              );
              actionCells.forEach((cell) => {
                cell.setAttribute("style", "visibility: visible;");
              });
            }
          },
          onMouseLeave: () => {
            if (document) {
              const actionCells = document.querySelectorAll(
                'td > span[style="visibility: visible;"]'
              );
              actionCells.forEach((cell) => {
                cell.setAttribute("style", "visibility: hidden;");
              });
            }
          },
        })}
      />
    </div>
  );
}
