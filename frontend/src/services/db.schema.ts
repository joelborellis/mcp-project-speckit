import Dexie from 'dexie';
import type { Table } from 'dexie';
import type { MCPEndpoint } from '../types/endpoint.types';

/**
 * MCPRegistryDB class
 * Defines IndexedDB schema for endpoint storage
 */
export class MCPRegistryDB extends Dexie {
  endpoints!: Table<MCPEndpoint, string>;
  
  constructor() {
    super('MCPRegistryDB');
    
    // Schema version 1
    this.version(1).stores({
      endpoints: 'id, status, submitterId, url, [status+submitterId], *tools'
    });
  }
}
