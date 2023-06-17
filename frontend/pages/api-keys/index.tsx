import React, { useState } from "react";
import {
  Table,
  message,
  Switch,
  InputNumber,
  Input,
  Button,
  Popconfirm,
  Space,
  Form,
  FormInstance,
} from "antd";
import useSWR, { mutate } from "swr";
import fetcher from "../../utils/fetcher";
import axios from "axios";
import { DateTime } from "luxon";

interface ApiKeyData {
  id: string;
  name: string;
  api_key_hint: string;
  valid_until: number;
  credits: number;
  enabled: boolean;
  requests: number; // This should be added to your data
}
interface EditableCellProps {
  editing: boolean;
  dataIndex: string;
  title: string;
  inputType: string;
  record: ApiKeyData;
  index: number;
  children: React.ReactNode;
  form: FormInstance;
}

// EditableCell component
const EditableCell: React.FC<EditableCellProps> = ({
  editing,
  dataIndex,
  title,
  inputType,
  record,
  index,
  children,
  form,
  ...restProps
}) => {
  let inputNode;
  if (inputType === "number") {
    inputNode = <InputNumber />;
  } else {
    inputNode = <Input />;
  }

  return (
    <td {...restProps}>
      {editing ? (
        <Form.Item
          name={dataIndex}
          style={{ margin: 0 }}
          rules={[
            {
              required: true,
              message: `Please Input ${title}!`,
            },
          ]}
        >
          {inputNode}
        </Form.Item>
      ) : (
        children
      )}
    </td>
  );
};

interface EditableRowProps {
  index: number;
}

const EditableRow: React.FC<EditableRowProps> = ({ index, ...props }) => {
  const [form] = Form.useForm();
  return (
    <Form form={form} component={false}>
      <tr {...props} />
    </Form>
  );
};

export default function ViewApiKeys() {
  const { data, error } = useSWR<ApiKeyData[]>("/admin/api-keys/", fetcher);
  const [editingKey, setEditingKey] = useState<string>("");

  const isEditing = (record: ApiKeyData) => record.id === editingKey;

  if (error) {
    message.error("An error occurred while fetching the data.");
    return <div>Failed to load</div>;
  }
  if (!data) return <div>Loading...</div>;

  const handleSwitchChange = async (record: ApiKeyData, checked: boolean) => {
    try {
      await axios.patch(`/admin/api-keys/${record.id}/`, { enabled: checked });
      message.success("Status updated successfully");
      mutate("/admin/api-keys/");
    } catch (error) {
      message.error("Failed to update status");
    }
  };

  const handleDelete = async (record: ApiKeyData) => {
    try {
      await axios.delete(`/admin/api-keys/${record.id}`);
      message.success("API Key deleted.");
      mutate("/admin/api-keys/");
    } catch (err) {
      message.error("Failed to delete API Key.");
    }
  };

  const save = async (form: FormInstance<any>, id: string) => {
    try {
      const row = await form.validateFields();
      await axios.patch(`/admin/api-keys/${id}/`, row);
      message.success("Successfully saved changes");
      setEditingKey("");
      mutate("/admin/api-keys/");
    } catch (err) {
      message.error("Failed to save changes");
    }
  };

  const columns = [
    {
      title: "ID",
      dataIndex: "id",
      key: "id",
    },
    {
      title: "Name",
      dataIndex: "name",
      key: "name",
      editable: true,
    },
    {
      title: "API Key Hint",
      dataIndex: "api_key_hint",
      key: "api_key_hint",
    },
    {
      title: "Valid Until",
      dataIndex: "valid_until",
      key: "valid_until",
      render: (text: number) =>
        text === -1
          ? "No Expiration"
          : DateTime.fromSeconds(text).toLocaleString(DateTime.DATETIME_MED),
      editable: true,
    },
    {
      title: "Credits",
      dataIndex: "credits",
      key: "credits",
      render: (text: number) => (text === -1 ? "Unlimited" : text),
      editable: true,
    },
    {
      title: "Enabled",
      dataIndex: "enabled",
      key: "enabled",
      render: (text: boolean, record: ApiKeyData) => (
        <Switch
          checked={text}
          onChange={(checked: boolean) => handleSwitchChange(record, checked)}
        />
      ),
    },

    {
      title: "Requests",
      dataIndex: "requests",
      key: "requests",
    },
    {
      title: "Operation",
      dataIndex: "operation",
      render: (_: unknown, record: ApiKeyData, index: number) => {
        const editable = isEditing(record);
        const cancel = () => {
          setEditingKey(""); // Exit the editing mode
        };
        return editable ? (
          <Space size="middle">
            <Form.Item shouldUpdate>
              {() => (
                <>
                  <a
                    onClick={async () => {
                      const form = formRef.current;
                      if (form) {
                        await save(form, record.id);
                      }
                    }}
                  >
                    Save
                  </a>
                  <a onClick={cancel}>Cancel</a>
                </>
              )}
            </Form.Item>
          </Space>
        ) : (
          <Space size="middle">
            <a
              disabled={editingKey !== ""}
              onClick={() => setEditingKey(record.id)}
            >
              Edit
            </a>
            <Popconfirm
              title="Sure to delete?"
              onConfirm={() => handleDelete(record)}
            >
              <a>Delete</a>
            </Popconfirm>
          </Space>
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
      onCell: (record: ApiKeyData) => ({
        record,
        form,
        inputType:
          col.dataIndex === "credits" || col.dataIndex === "valid_until"
            ? "number"
            : "text",
        dataIndex: col.dataIndex,
        title: col.title,
        editing: isEditing(record),
      }),
    };
  });

  return (
    <div style={{ padding: "2em" }}>
      <Button
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
        Create New
      </Button>
      <Table
        components={{
          body: {
            cell: EditableCell,
            row: EditableRow,
          },
        }}
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
