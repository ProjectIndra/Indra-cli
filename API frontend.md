### **UI API Endpoints List**

The application communicates with two primary backend servers: the **Main Management Server** (referenced as `MG_SERVER`) and the **Monitoring Server** (referenced as `MONITORING_SERVER`).

#### **1. VM Management (`/vms`)**
| Method | Endpoint | Description | Payload |
| :--- | :--- | :--- | :--- |
| **GET** | `/vms/allVms` | List all VMs | `?vmName={name}` (Optional query param) |
| **POST** | `/vms/launch` | Create/Launch a new VM | `{ vcpus, ram, storage, vm_image, provider_id, provider_user_id, vm_name, provider_name }` |
| **POST** | `/vms/start` | Start a VM | `{ vm_id, provider_id }` |
| **POST** | `/vms/stop` | Stop a VM | `{ vm_id, provider_id }` |
| **POST** | `/vms/remove` | Delete a VM | `{ vm_id, provider_id }` |

#### **2. Storage / HDFS (`/hdfs`)**
| Method | Endpoint | Description | Payload |
| :--- | :--- | :--- | :--- |
| **GET** | `/hdfs/list` | List directory contents | `?path={path}` |
| **POST** | `/hdfs/mkdir` | Create a new directory | `{ path }` |
| **POST** | `/hdfs/delete` | Delete files/folders | `{ paths: [...] }` |
| **POST** | `/hdfs/rename` | Rename a file/folder | `{ old_path, new_name }` |
| **POST** | `/hdfs/uploadFileFolder` | Upload file or folder | `FormData` (contains `file`, `path`, `type`) |
| **GET** | `/hdfs/download` | Download a file | `?path={path}` (Triggered via link) |

#### **3. Provider Management (`/ui/providers` & `/providerServer`)**
| Method | Endpoint | Description | Payload |
| :--- | :--- | :--- | :--- |
| **GET** | `/ui/providers/userProviderDetails` | Get user's provider list | None |
| **POST** | `/ui/providers/providerClientDetails` | Get active clients for a provider | `{ providerId }` |
| **POST** | `/ui/providers/update_config` | Update provider configuration | `{ providerName, providerId, providerAllowedVcpu, ... }` |
| **POST** | `/providers/query` | Check if VM creation is possible | `{ vcpus, ram, storage, vm_image, provider_id, provider_user_id }` |
| **POST** | `/providerServer/getProviderVerificationToken` | Get token to add a new provider | `{ user_id, providerId }` |
| **DELETE** | `/ui/providers/{id}` | Delete a provider | None (ID in URL) |

#### **4. CLI & Tunnel Management (`/ui`)**
| Method | Endpoint | Description | Payload |
| :--- | :--- | :--- | :--- |
| **GET** | `/ui/getAllCliSessionDetails` | List all CLI sessions | None |
| **GET** | `/ui/getCliV
erificationToken` | Get token for CLI verification | None |
| **GET** | `/ui/deleteCliSession` | Delete a CLI session | `?cli_id={id}` |
| **POST** | `/ui/getUserClients` | List user tunnels | None |
| **POST** | `/ui/createTunnelClient` | Create a new tunnel | `{ tunnelName }` |
| **POST** | `/ui/editTunnel` | Edit tunnel name | `{ tunnelId, tunnelName }` |
| **POST** | `/ui/deleteTunnel` | Delete a tunnel | `{ tunnelId }` |

#### **5. User Authentication**
| Method | Endpoint | Description | Payload |
| :--- | :--- | :--- | :--- |
| **POST** | `/login` | User login | `{ username_or_email, password }` |
| **POST** | `/register` | User registration | `{ email, username, password }` |
| **GET** | `/ui/profile/getUserDetails` | Get current user's profile | None |
| **PUT** | `/ui/profile/updateUserDetails` | Update user profile | `{ username, email, ... }` |

#### **6. Monitoring & Dashboards (`/dashboard`)**
*These calls are directed to the Monitoring Server.*
| Method | Endpoint | Description | Payload |
| :--- | :--- | :--- | :--- |
| **GET** | `/dashboard/listDashboards` | Get all dashboards | None |
| **POST** | `/dashboard/createDashboard` | Create a dashboard | `{ dashboardName, dashboardDescription }` |
| **POST** | `/dashboard/updateDashboard` | Update dashboard info | `{ dashboardId, dashboardName, dashboardDescription }` |
| **POST** | `/dashboard/deleteDashboard` | Delete a dashboard | `{ dashboardId }` |
| **POST** | `/dashboard/listGraphsForDashboard` | List graphs in a dashboard | `{ dashboardId }` |
| **POST** | `/dashboard/getGraphPoints` | Get data points for a graph | Full graph object (normalized) |
| **POST** | `/dashboard/createGraphWithSeries` | Create a new graph | `{ dashboardId, graphDetails, series... }` |
| **POST** | `/dashboard/deleteGraph` | Delete a graph | `{ graphId }` |
| **POST** | `/dashboard/getServiceDetailsForUser` | Get service metrics | None |

### **Notes:**
- **Main Server (`Api.js`)**: Uses an `apiCall(method, endpoint, data)` wrapper. Most endpoints are prefixed with `/ui` or `/vms`.
- **Monitoring Server (`apiServices.js`)**: Uses a direct `axios` instance with standardized dashboard endpoints.
- **Headers**: All calls include a `Bearer` token (either from `document.cookie`, `sessionStorage`, or `localStorage`) and an `ngrok-skip-browser-warning` header.