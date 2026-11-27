// Esqueleto generado por spec2code. Módulo: Misiones y progresión
// NO es una solución: clases y firmas con TODO. Completa la lógica y audita contra la spec.
package rpgmanager.misionesyprogresion;

import java.util.ArrayList;
import java.util.List;

/** Personaje. Trazabilidad: RF-01, RF-02, RF-03, RF-04, RF-06, RF-08, RF-09. */
public class Personaje {
    private int idPersonaje;
    private String nombre;
    private int nivel;
    private int experienciaDisponible;
    private List<IntentoMision> intentoMisions = new ArrayList<>(); // asociacion ()

    public Personaje(int idPersonaje, String nombre, int nivel, int experienciaDisponible) {
        this.idPersonaje = idPersonaje;
        this.nombre = nombre;
        this.nivel = nivel;
        this.experienciaDisponible = experienciaDisponible;
    }

    // TODO: getters y setters (encapsulamiento)

    /** consultar_misiones_disponibles (RF-01). */
    public List<Object> consultarMisionesDisponibles() {
        throw new UnsupportedOperationException("TODO: implementar Personaje.consultar_misiones_disponibles");
    }

    /** aceptar_mision (RF-02). */
    public void aceptarMision() {
        throw new UnsupportedOperationException("TODO: implementar Personaje.aceptar_mision");
    }

    /** consultar_avance (RF-03). */
    public void consultarAvance() {
        throw new UnsupportedOperationException("TODO: implementar Personaje.consultar_avance");
    }

    /** completar_mision (RF-04). */
    public void completarMision() {
        throw new UnsupportedOperationException("TODO: implementar Personaje.completar_mision");
    }

    /** otorgar_experiencia (RF-05). */
    public void otorgarExperiencia() {
        throw new UnsupportedOperationException("TODO: implementar Personaje.otorgar_experiencia");
    }

    /** verificar_subida_nivel (RF-07). */
    public void verificarSubidaNivel() {
        throw new UnsupportedOperationException("TODO: implementar Personaje.verificar_subida_nivel");
    }

    /** consultar_progresion (RF-06). */
    public void consultarProgresion() {
        throw new UnsupportedOperationException("TODO: implementar Personaje.consultar_progresion");
    }

    /** consultar_historial (RF-08). */
    public void consultarHistorial() {
        throw new UnsupportedOperationException("TODO: implementar Personaje.consultar_historial");
    }

    /** abandonar_mision (RF-09). */
    public void abandonarMision() {
        throw new UnsupportedOperationException("TODO: implementar Personaje.abandonar_mision");
    }
}
