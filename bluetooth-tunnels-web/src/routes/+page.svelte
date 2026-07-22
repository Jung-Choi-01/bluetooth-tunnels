<script lang="ts">
  import { onMount } from "svelte";
  import { asset } from '$app/paths';

  type RequestConfig = {
    type: string;
    value: string;
  };
  type DeviceConfig = Map<string, RequestConfig>;
  type Config = Map<string, DeviceConfig>;
  type RequestStatus = "idle" | "waiting..." | "success" | "failed";
  type RawRequestConfig = Record<string, string>;
  type ConfigJson = Record<string, Record<string, RawRequestConfig>>;

  let url = $state("");
  let device = $state("");
  let config: Config | null = $state(null);
  let status: RequestStatus = $state("idle");

  function parseConfig(json: ConfigJson): Config {
    return new Map(
      Object.entries(json).map(([deviceId, requests]) => [
        deviceId,
        new Map(
          Object.entries(requests).map(([requestId, requestConfig]) => {
            const [type, value] = Object.entries(requestConfig)[0] ?? ["", ""];

            return [requestId, { type, value } satisfies RequestConfig] as [
              string,
              RequestConfig,
            ];
          }),
        ),
      ]),
    );
  }

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

  onMount(async () => {
    const response = await fetch(asset('/message_config.json'));
    const json = await response.json();
    config = parseConfig(json as ConfigJson);
    console.log(config);
  });
</script>

<div style="display:flex; flex-direction:column; align-items:center; justify-content:center; gap:10px;">
  <div>
    <input bind:value={url} placeholder="URL" />
    <select bind:value={device}>
      {#if config}
        {#each Array.from(config.keys()) as deviceId}
          <option value={deviceId}>{deviceId}</option>
        {/each}
      {/if}
    </select>
  </div>

  <div>Status: {status}</div>

  {#if config && device}
    {@const requests = config.get(device)}
    {#if requests}
      {#each Array.from(requests.entries()) as [requestId, requestConfig]}
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
