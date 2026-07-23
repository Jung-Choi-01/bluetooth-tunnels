<script lang="ts">
  import json from "../message_config.json";

  type RequestConfig = {
    type: string;
    value: string;
  };
  type DeviceConfig = Record<string, RequestConfig>;
  type Config = Record<string, DeviceConfig>;
  type RequestStatus = "idle" | "waiting..." | "success" | "failed";

  let url = $state("");
  let device = $state("");
  const config: Config = json as Config;
  let status: RequestStatus = $state("idle");

  function buildRequestUrl(deviceId: string, requestId: string, value?: string) {
    const path = value === undefined
      ? `${url}/${encodeURIComponent(deviceId)}/${encodeURIComponent(requestId)}`
      : `${url}/${encodeURIComponent(deviceId)}/${encodeURIComponent(requestId)}/${encodeURIComponent(value)}`;

    return new Request(path, { method: "POST" });
  }

  async function makeRequest(deviceId: string, requestId: string, value?: string) {
	if(!url) return;
    const request = buildRequestUrl(deviceId, requestId, value);
    status = "waiting...";

    try {
      const response = await fetch(request);
      status = response.ok ? "success" : "failed";
    } catch {
      status = "failed";
    }
  }

  function handleRangeInput(event: Event, deviceId: string, requestId: string) {
    const target = event.currentTarget as HTMLInputElement;
    void makeRequest(deviceId, requestId, target.value);
  }
</script>

<div style="display:flex; flex-direction:column; align-items:center; justify-content:center; gap:10px;">
  <div>
    <input bind:value={url} placeholder="URL" />
    <select bind:value={device}>
      {#if config}
        {#each Object.entries(config) as [deviceId]}
          <option value={deviceId}>{deviceId}</option>
        {/each}
      {/if}
    </select>
  </div>

  <div>Status: {status}</div>

  {#if config && device}
    {@const requests = config[device]}
    {#if requests}
      {#each Object.entries(requests) as [requestId, requestConfig]}
        <div>
          <span>{requestId}</span>:
          {#if requestConfig.type === "range"}
            <input
              type="range"
              oninput={(event) => handleRangeInput(event, device, requestId)}
            />
		  {:else}
			input type {requestConfig.type} not found!
          {/if}
        </div>
      {/each}
    {/if}
  {/if}
</div>
