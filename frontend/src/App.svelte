<script>
  import { Router, Route } from 'svelte-routing'
  import { sesion } from './lib/stores.js'
  import Layout from './components/Layout.svelte'
  import Protegida from './components/Protegida.svelte'
  import Toasts from './components/Toasts.svelte'
  import Login from './pages/Login.svelte'
  import Inicio from './pages/Inicio.svelte'
  import Solicitudes from './pages/Solicitudes.svelte'
  import SolicitudDetalle from './pages/SolicitudDetalle.svelte'
  import Notificaciones from './pages/Notificaciones.svelte'
  import Usuarios from './pages/Usuarios.svelte'
  import Categorias from './pages/Categorias.svelte'
  import Parametros from './pages/Parametros.svelte'
  import Reportes from './pages/Reportes.svelte'

  export let url = ''
  const ADMIN = ['ADMINISTRADOR']
  const STAFF = ['ADMINISTRADOR', 'SUPERVISOR']
</script>

<Router {url}>
  {#if !$sesion}
    <Route path="/*" component={Login} />
  {:else}
    <Layout>
      <Route path="/" component={Inicio} />
      <Route path="/inicio" component={Inicio} />
      <Route path="/solicitudes" component={Solicitudes} />
      <Route path="/solicitudes/:id" let:params><SolicitudDetalle id={params.id} /></Route>
      <Route path="/notificaciones" component={Notificaciones} />
      <Route path="/usuarios"><Protegida roles={ADMIN}><Usuarios /></Protegida></Route>
      <Route path="/categorias"><Protegida roles={ADMIN}><Categorias /></Protegida></Route>
      <Route path="/parametros"><Protegida roles={ADMIN}><Parametros /></Protegida></Route>
      <Route path="/reportes"><Protegida roles={STAFF}><Reportes /></Protegida></Route>
    </Layout>
  {/if}
</Router>
<Toasts />
