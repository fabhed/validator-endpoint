import { Button, Input, Space, theme } from "antd";
import { useEffect, useRef, useState } from "react";
import {
  EditOutlined,
  CloseOutlined,
  LoadingOutlined,
  SaveOutlined,
} from "@ant-design/icons";
import { useToken } from "antd/es/theme/internal";

interface EditableFieldProps {
  initialValue: any; // we don't know the type of value, it could be string, number, etc.
  name: string;
  onUpdate: (value: any) => Promise<void>; // assumes onUpdate is async and doesn't return anything
  /**
   * onChange is called when the user types in the input field.
   */
  onChange: (value: any) => void;
  onCancel: () => void;
  /**
   * Should the value be displayed as an input field when not editing?
   * Defaults to false.
   */
  displayValueAsInput?: boolean;
}

// Usage in the component declaration
export const EditableField: React.FC<EditableFieldProps> = ({
  initialValue,
  name,
  onUpdate,
  onCancel,
  onChange,
  displayValueAsInput = false,
}) => {
  const [editing, setEditing] = useState(false);
  const [value, setValue] = useState<any>(initialValue);
  const [loading, setLoading] = useState(false);
  const [unchangedValue, setUnchangedValue] = useState<any>();
  const inputRef = useRef(null);
  const {
    token: { colorPrimary },
  } = theme.useToken();

  useEffect(() => {
    setValue(initialValue);
    setUnchangedValue(initialValue);
  }, [initialValue]);

  const toggleEdit = () => {
    setEditing(!editing);
  };

  const handleCancel = () => {
    setValue(unchangedValue);
    onChange(unchangedValue);
    onCancel();
    toggleEdit();
  };

  const save = async () => {
    try {
      setLoading(true);
      await onUpdate(value);
      toggleEdit();
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (editing) {
    return (
      <Space.Compact>
        <Input
          ref={inputRef}
          value={value}
          onPressEnter={() => save()}
          onChange={(e) => {
            setValue(e.target.value);
            onChange(e.target.value);
          }}
          style={{ minWidth: 200 }}
          autoFocus
        />
        <Button onClick={() => save()} disabled={loading}>
          <Space>
            <span>Save</span>
            {loading ? <LoadingOutlined /> : <SaveOutlined />}
          </Space>
        </Button>
        <Button onClick={handleCancel} disabled={loading}>
          <Space>
            <span>Cancel</span>
            <CloseOutlined />
          </Space>
        </Button>
      </Space.Compact>
    );
  } else {
    return displayValueAsInput ? (
      <Space.Compact>
        <Input value={value} disabled style={{ minWidth: 200 }} />
        <Button onClick={toggleEdit}>
          <Space>
            <span>Edit</span>
            <EditOutlined />
          </Space>
        </Button>
      </Space.Compact>
    ) : (
      <div style={{ display: "flex", alignItems: "center" }}>
        <span>{value}</span>
        <EditOutlined
          style={{ marginLeft: 8, cursor: "pointer" }}
          onClick={toggleEdit}
        />
      </div>
    );
  }
};
