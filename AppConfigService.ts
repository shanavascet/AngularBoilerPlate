@Injectable({ providedIn: 'root' })
export class AppConfigService {
  private config: any;

  setConfig(config: any): void {
    this.config = config;
  }

  get(key: string): any {
    return this.config?.[key];
  }
}
